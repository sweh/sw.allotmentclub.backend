# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ..log import user_data_log, log_with_user
from .base import date_time, format_size, format_mimetype
from io import BytesIO
from pyramid.response import FileIter
from pyramid.view import view_config
from sw.allotmentclub import Depot, User
import datetime
import sw.allotmentclub.browser.base


class Query(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Größe': format_size,
        'Dateityp': format_mimetype,
        'Aktualisiert': date_time,
    }

    data_class = {
        'Dateiname': 'expand'
    }
    data_hide = {
        'Dateityp': 'phone,tablet',
        'Größe': 'phone,tablet',
        'Aktualisiert': 'phone,tablet',
        'Von': 'phone,tablet',
    }

    def select(self):
        return (
            self.db.query(
                Depot.id.label('#'),
                Depot.name.label('Dateiname'),
                Depot.mimetype.label('Dateityp'),
                Depot.size.label('Größe'),
                Depot.date.label('Aktualisiert'),
                User.username.label('Von'))
            .select_from(Depot)
            .join(User))


@view_config(route_name='depots', renderer='json',
             permission='view')
class DepotListView(sw.allotmentclub.browser.base.TableView):
    """ Liste aller Depots."""

    query_class = Query
    default_order_by = 'name'
    available_actions = [
        dict(url='depot_add', btn_class='btn-success', icon='fa fa-plus',
             title='Neu'),
        dict(url='depot_edit', btn_class='btn-success', icon='fa fa-pencil',
             title='Bearbeiten'),
        dict(url='depot_delete', btn_class='btn-danger',
             icon='glyphicon glyphicon-trash', title='Löschen'),
        dict(url='depot_download', btn_class='btn-success',
             icon='fa fa-download', title='Herunterladen')]


class DepotBase(sw.allotmentclub.browser.base.View):

    def parse_file(self):
        file = self.request.params.get('file')
        data = file.file
        data.seek(0)
        data = data.read()
        name = file.filename
        mimetype = file.type
        size = len(data)
        date = datetime.datetime.now()
        user = self.request.user
        return name, mimetype, size, data, date, user

    def log(self, id):
        log_with_user(user_data_log.info,
                      self.request.user,
                      'hat Ablage %s %s.', id, self.action)


@view_config(route_name='depot_add', renderer='json',
             permission='view')
class DepotAddView(DepotBase):

    action = 'hinzugefügt'

    def __call__(self):
        if not self.form_submit():
            return {'status': 'success', 'data': {}}
        name, mimetype, size, data, date, user = self.parse_file()
        depot = Depot.create(
            name=name, mimetype=mimetype, size=size, data=data,
            date=date, user=user)
        depot.commit()
        self.log(depot.id)
        return {'status': 'success'}


@view_config(route_name='depot_edit', renderer='json',
             permission='view')
class DepotEditView(DepotBase):

    action = 'bearbeitet'

    def __call__(self):
        if not self.form_submit():
            return {'status': 'success', 'data': {}}
        name, mimetype, size, data, date, user = self.parse_file()
        if mimetype != self.context.mimetype:
            return {'status': 'error',
                    'message': 'Kann nur Dateien vom gleichen Typ bearbeiten. '
                               'alt: {}, neu: {}'.format(
                                   self.context.mimetype, mimetype)}
        self.context.size = size
        self.context.data = data
        self.context.date = date
        self.context.name = name
        self.context.user = user
        self.log(self.context.id)
        return {'status': 'success'}


@view_config(route_name='depot_delete', renderer='json',
             permission='view')
class DepotDeleteView(sw.allotmentclub.browser.base.DeleteView):

    model = Depot


@view_config(route_name='depot_download',
             permission='view')
class DepotDownloadView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = self.context.mimetype
        response.content_length = int(self.context.size)
        response.content_disposition = (
            'attachment; filename=%s' % self.context.name)
        response.app_iter = FileIter(BytesIO(self.context.data))
        return response
