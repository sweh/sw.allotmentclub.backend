# encoding=utf-8
from ..log import app_log
from .base import string_agg, date, boolean, route_url
from .depot import DepotBase
from datetime import datetime
from io import BytesIO
from pyramid.response import FileIter
from pyramid.response import Response
from pyramid.view import view_config
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
from svglib.svglib import svg2rlg
from sw.allotmentclub import Parcel, Allotment, Member
import os
import pkg_resources
import sw.allotmentclub.browser.base
import tempfile


class Query(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Karte hinterlegt': boolean,
    }

    def select(self):
        return (
            self.db.query(
                Parcel.id.label('#'),
                Parcel.number.label('Flurstück'),
                string_agg(Allotment.number).label('Bungalow'),
                Member.lastname.label('Nachname'),
                Member.firstname.label('Vorname'),
                Parcel.map_mimetype.label('Karte hinterlegt'),
            )
            .select_from(Parcel)
            .join(Allotment)
            .join(Member)
            .group_by(
                Parcel.id,
                Parcel.number,
                Member.firstname,
                Member.lastname,
                Parcel.map_mimetype,
            ))


@view_config(route_name='map', renderer='json', permission='view')
class MapView(sw.allotmentclub.browser.base.TableView):

    query_class = Query
    available_actions = [
        dict(url='map_download', btn_class='btn-success',
             icon='fa fa-download', title='Herunterladen')]

    def __call__(self):
        result = super(MapView, self).__call__()
        map_data = {}
        for _, parcel, allotment, ln, fn, _ in sw.allotmentclub.json_result(
                result['data']['data']):
            if fn:
                ln += ', {}.'.format(fn[0])
            if str(parcel) not in map_data:
                map_data[str(parcel)] = [str(allotment), ln]
            elif map_data[str(parcel)][1] == ln:
                map_data[str(parcel)] = [
                    map_data[str(parcel)][0] + f', {allotment}',
                    map_data[str(parcel)][1]
                ]
            else:
                map_data[str(parcel)] = [
                    map_data[str(parcel)][0] + f', {allotment}',
                    map_data[str(parcel)][1] + f', {ln}'
                ]
        result['data']['map_data'] = map_data
        with open(pkg_resources.resource_filename(
                'sw.allotmentclub.browser', 'lageplan.svg')) as map_:
            result['data']['map'] = map_.read()
        return result


@view_config(route_name='map_download', permission='view')
class MapDownloadView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        data = self.request.POST['svg']
        msg = 'Lageplan vom %s' % date(datetime.now())
        svg_handle, svg_filename = tempfile.mkstemp(suffix='svg')
        app_log.info('Map written to `{}`.'.format(svg_filename))
        try:
            os.fdopen(svg_handle, 'wb').write(data.encode('utf-8'))
            d = renderPDF.renderScaledDrawing(svg2rlg(svg_filename))
            output = BytesIO()
            c = Canvas(output)
            c.setTitle(msg)
            c.setPageSize((d.width, d.height))
            renderPDF.draw(d, c, 0, 0)
            c.showPage()
            c.save()
        finally:
            os.remove(svg_filename)
        output.seek(0)
        data = output.read()
        return Response(
            content_type='application/pdf',
            content_disposition='attachment; filename="Lageplan.pdf"',
            content_length=len(data),
            charset=b'utf-8',
            body=data)


@view_config(route_name='parcel_list', renderer='json', permission='view')
class ParcelListView(sw.allotmentclub.browser.base.TableView):

    query_class = Query
    available_actions = [
        dict(url='parcel_map_upload', btn_class='btn-success',
             icon='fa fa-upload', title='Hinterlegen'),
        dict(url='parcel_map_download_check', btn_class='btn-success',
             icon='fa fa-download', title='Herunterladen')]


@view_config(route_name='parcel_map_upload', renderer='json',
             permission='view')
class ParcelMapAddView(DepotBase):

    action = 'eine Karte hinzugefügt'

    def __call__(self):
        if not self.form_submit():
            return {'status': 'success', 'data': {}}
        name, mimetype, size, data, date, user = self.parse_file()
        self.context.map_mimetype = mimetype
        self.context.map_size = size
        self.context.map_data = data
        self.log(self.context.id)
        return {'status': 'success'}


@view_config(
    route_name='parcel_map_download_check',
    permission='view',
    renderer='json')
class ParcelMapDownloadCheckView(sw.allotmentclub.browser.base.View):

    def update(self):
        if not self.context.map_mimetype:
            self.result = {
                'status': 'error',
                'message': 'Kein Anhang zum Download vorhanden'
            }
        else:
            download_url = (
                '/api' + route_url('parcel_map_download', self.request))
            download_url = download_url.replace('{id}', str(self.context.id))
            self.result = {
                'status': 'success',
                'redirect': download_url
            }


@view_config(route_name='parcel_map_download', permission='view')
class ParcelMapDownloadView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = self.context.map_mimetype
        response.content_length = int(self.context.map_size)
        response.content_disposition = 'attachment; filename=%s_map.%s' % (
            self.context.number,
            self.context.map_mimetype.split('/')[1]
        )
        response.app_iter = FileIter(BytesIO(self.context.map_data))
        return response
