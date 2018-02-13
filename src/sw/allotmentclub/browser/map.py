# encoding=utf-8
from __future__ import unicode_literals
from ..log import app_log
from .base import string_agg, date
from io import BytesIO
from pyramid.response import Response
from pyramid.view import view_config
from sw.allotmentclub import Parcel, Allotment, Member
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
from datetime import datetime
import pkg_resources
import sw.allotmentclub.browser.base
import tempfile
import os


class Query(sw.allotmentclub.browser.base.Query):

    def select(self):
        return (
            self.db.query(
                Parcel.number.label('Flurstück'),
                string_agg(Allotment.number).label('Bungalow'),
                Member.lastname.label('Nachname'),
                Member.firstname.label('Vorname'),
            )
            .select_from(Parcel)
            .join(Allotment)
            .join(Member)
            .group_by(Parcel.number, Member.firstname, Member.lastname))


@view_config(route_name='map', renderer='json', permission='view')
class MapView(sw.allotmentclub.browser.base.TableView):

    query_class = Query
    available_actions = [
        dict(url='map_download', btn_class='btn-success',
             icon='fa fa-download', title='Herunterladen')]

    def __call__(self):
        result = super(MapView, self).__call__()
        map_data = {}
        for parcel, allotment, ln, fn in sw.allotmentclub.json_result(
                result['data']['data']):
            if fn:
                ln += ', {}.'.format(fn[0])
            map_data[str(parcel)] = [str(allotment), ln]
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
            c.setPageSize((d.width + 1000, d.height - 300))
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
