# coding:utf-8
from __future__ import unicode_literals
from ..log import auth_log, log_with_user
from .. import User, DashboardData
from datetime import datetime
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config, forbidden_view_config
import hashlib
import pyramid.httpexceptions
import pyramid.security
import sw.allotmentclub.browser.app
import sw.allotmentclub.browser.auth
import sw.allotmentclub.browser.base
import sw.allotmentclub.version
import urllib.parse


# Number of failed logins before the account gets locked.
MAX_FAILED_LOGINS = 3

SESSION_TIMEOUT = 'Ihre Sitzung wurde aufgrund zu langer Inaktivität '\
                  'automatisch beendet. Bitte melden Sie sich erneut an.'


@forbidden_view_config(renderer='json')
class Forbidden(sw.allotmentclub.browser.app.HTTPError):

    def __call__(self):
        # respond with HTTPForbidden if user is authenticated
        # use unauthenticated_userid to circumvent privilege check,
        # which would raise another HTTPForbidden
        if pyramid.security.unauthenticated_userid(self.request):
            return super(Forbidden, self).__call__()

        if getattr(self.request, 'session_timeout', False):
            self.request.session.flash(SESSION_TIMEOUT, 'error')

        return {'status': 'error', 'message': 'Zugriff verweigert.'}

    # called from superclass .app.Error
    def log(self):
        auth_log.warning(
            'Ref: %s User %s is not allowed to access %s',
            self.error_ref, self.request.user.username, self.request.url)


def get_next_url(request, default_url):
    parsed_url = urllib.parse.urlparse(request.url)
    query = urllib.parse.parse_qs(parsed_url.query)
    if 'came_from' in query:
        next_url = u'{}://{}{}'.format(
            parsed_url.scheme,
            parsed_url.netloc,
            query['came_from'][0])
    else:
        next_url = default_url
    return next_url


class NetatmoMixin():

    def get_temp_data(self, dest='rotersee'):
        data = (DashboardData.query()
                .filter(getattr(DashboardData, '{}_out_temp'.format(dest)).isnot(None))
                .order_by(DashboardData.date.desc()).first())
        if data is None:
            return dict()
        return dict(temperature=getattr(data, '{}_out_temp'.format(dest)),
                    trend=getattr(data, '{}_out_temp_trend'.format(dest)),
                    date=data.date.strftime('%d.%m.%Y %H:%M Uhr'),
                    sum_rain_24=getattr(data, '{}_rain_24'.format(dest)))


@view_config(route_name='login',
             permission=NO_PERMISSION_REQUIRED,
             renderer='json')
class LoginView(sw.allotmentclub.browser.base.View, NetatmoMixin):

    def get_user_data(self, user):
        gravatar_url = 'https://www.gravatar.com/avatar/%s' % (
            hashlib.md5(user.email.encode('utf-8')).hexdigest())
        return dict(username=user.username,
                    name='%s %s' % (user.vorname, user.nachname),
                    gravatar=gravatar_url)

    def __call__(self):
        result = self.login()
        result['version'] = sw.allotmentclub.version.__version__
        return result

    def login(self):
        if self.request.params.get('to'):
            # timeout occured, redirected from a javascript json request
            self.request.session.flash(SESSION_TIMEOUT, 'error')

        if self.request.session.get('auth.userid'):
            user = User.get(self.request.session['auth.userid'])
            if user is not None:
                return dict(status='success',
                            message='Ihre Sitzung wurde wiederhergestellt.',
                            user=self.get_user_data(user),
                            temp=self.get_temp_data())

        if (self.request.method != 'POST' or
                not self.request.params.get('username')):
            self.update()
            return dict(status='error', message='')

        username = self.request.params.get('username').lower()
        password = self.request.params.get('password')

        user, authenticated = sw.allotmentclub.browser.auth.login(
            username, password)
        if authenticated and user and not user.is_locked:
            self.request.session.invalidate()
            pyramid.security.remember(self.request, user.id)
            msg = u'Anmeldung erfolgreich.'
            log_with_user(
                auth_log.info, user, 'hat sich angemeldet.')
            if user.last_login is not None:
                msg = ('{} Das letzte Mal waren Sie hier {}.'.format(
                    msg, user.last_login.strftime('am %d.%m.%Y um %H:%M Uhr')))
            user.last_login = datetime.now()
            if user.failed_logins:
                if user.failed_logins == 1:
                    tmp_msg = 'wurde {} fehlgeschlagener Anmeldeversuch'
                else:
                    tmp_msg = 'wurden {} fehlgeschlagene Anmeldeversuche'
                msg = ('{} Es {} seit Ihrer letzten Anmeldung '
                       'aufgezeichnet.'.format(
                           msg, tmp_msg.format(user.failed_logins)))
                user.failed_logins = 0
            default_url = self.request.route_url('login')
            next_url = get_next_url(self.request, default_url)
            return dict(status='success', message=msg, next_url=next_url,
                        user=self.get_user_data(user),
                        temp=self.get_temp_data())
        else:
            msg = u'Anmeldung fehlgeschlagen.'
            if user:
                log_with_user(
                    auth_log.info, user,
                    'Anmeldung fehlgeschlagen (falsches Passwort) für %s',
                    user.username)
                user.failed_logins += 1
                if user.failed_logins >= MAX_FAILED_LOGINS:
                    user.lock('MAXLOGINS')
                    log_with_user(
                        auth_log.warning, user,
                        'Accout %s gesperrt: %s fehlerhafte Logins.',
                        user.username, user.failed_logins)
                if user.is_locked:
                    msg = ('{} Ihr Account wurde gesperrt: {}'.format(
                        msg, user.is_locked))
            else:
                auth_log.info(
                    'Anmeldung fehlgeschlagen (falscher Benutzername) für %s',
                    username)

            return dict(status='error', message=msg)


@view_config(route_name='logout', renderer='json',
             permission=NO_PERMISSION_REQUIRED)
def logout_view(request, message=None):
    log_with_user(
        auth_log.info, request.user, 'hat sich abgemeldet.')
    pyramid.security.forget(request)
    # Cannot use delete(), since flash message will not be displayed
    # (Reason not known, but delete isn't in ISession anyway)
    request.session.invalidate()
    if message is None:
        status, message = (
            'success',
            u'Abmeldung abgeschlossen. Sie können sich nun erneut anmelden.')
    else:
        status, message = message
    return dict(status=status, message=message,
                version=sw.allotmentclub.version.__version__)
