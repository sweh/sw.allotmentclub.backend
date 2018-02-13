from pyramid.security import Allow, Authenticated
from sw.allotmentclub import User, AccessAuthority
import pyramid.httpexceptions
import pyramid.security
import pyramid.threadlocal


def authorize(request=None, context=None):
    if request is None:
        request = pyramid.threadlocal.get_current_request()
    route_name = request.matched_route.name
    user = request.user
    if context is not None:
        if user.organization_id != context.organization_id:
            return []
    allowed = (AccessAuthority.query()
               .filter(AccessAuthority.viewname == route_name)
               .filter(AccessAuthority.user == user).all())
    if user.unrestricted_access or allowed:
        return [(Allow, Authenticated, 'view')]
    return []


class DefaultContext(object):

    @property
    def __acl__(self):
        return authorize(self.request)

    def __init__(self, request):
        self.request = request


def get_default_context(request):
    return DefaultContext(request)


def login(login, password):
    """Try to verify the user.

    Returns (User, authenticated?)

    User will be None if password is missing or user does not exist,
    otherwise the object will be retrieved from the database.

    authenticated? will be True iff check_password succeeds
    and False otherwise.
    """
    user = None
    if login:
        user = User.by_username(login)
    if user and password:
        return (user, user.check_password(password))

    return (None, False)


def get_user(request):
    user_id = pyramid.security.authenticated_userid(request)
    if user_id:
        return User.get(user_id)
    else:
        return User()
