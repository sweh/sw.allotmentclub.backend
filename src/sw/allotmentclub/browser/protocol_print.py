# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .protocol import format_markdown
from io import BytesIO
from pyramid.view import view_config
from PyPDF2 import PdfFileWriter, PdfFileReader
from .mail import append_pdf
import datetime
import img2pdf
import pybars
import sw.allotmentclub.browser.base
import xhtml2pdf.pisa


TEMPLATE = """
<html lang=de>
  <head>
    <meta charset="utf-8" />
    <style>
      @page {
        size: a4 portrait;
        @frame content_frame {
            left: 50pt; width: 512pt; top: 50pt; height: 692pt;
        }
      }
      body { font-size: 10pt; }
    </style>
  </head>
  <body>
    <h1>{{type}}</h1>
    <h3>{{title}}</h3>
    Datum: {{day}}<br />
    Teilnehmer: {{attendees}}<br />
    Ort: {{location}}<br />
    <hr />
    <table>
      <thead>
        <tr>
          <th style="width: 7%; text-align:left">Zeit</th>
          <th style="width: 85%; text-align:left">TOP</th>
          <th style="width: 8%; text-align:right">Verantw.</th>
        </tr>
      </thead>
    </table>
    <hr />
    {{#each details}}
    <table>
      <tbody>
          <tr>
            <td style="width: 7%; vertical-align: top;">{{time}}</td>
            <td style="width: 85%">{{{message}}}</td>
            <td style="width: 8%; vertical-align: top;">{{{responsible}}}</td>
          </tr>
      </tbody>
    </table>
    <hr />
    {{/each}}

    {{#if commitments}}
    <pdf:nextpage />
    <h3>Absprachen</h3>
    <hr />
    <table>
      <thead>
        <tr>
          <th style="width: 7%; text-align:left">Wer?</th>
          <th style="width: 80%; text-align:left">Was?</th>
          <th style="width: 13%; text-align:left">Bis wann?</th>
        </tr>
      </thead>
      <tbody>
        {{#each commitments}}
          <tr>
            <td style="width: 7%; vertical-align: top;">{{who}}</td>
            <td style="width: 80%">{{{what}}}</td>
            <td style="width: 13%; vertical-align: top;">{{when}}</td>
          </tr>
        {{/each}}
      </tbody>
    </table>
    {{/if}}

    {{#if attachments}}
    <pdf:nextpage />
    <h3>Anlagen</h3>
    {{/if}}
  </body>
</html>"""


@view_config(route_name='protocol_print', permission='view')
class ProtocolPrintView(sw.allotmentclub.browser.base.PrintBaseView):

    filename = 'Protokoll'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_pdf(self):
        # Base data
        data = self.get_json(self.context)
        # Details data
        data['details'] = []
        time = self.context.day
        minutes = 0
        for detail in self.context.details:
            detail = self.get_json(detail)
            time += datetime.timedelta(minutes=minutes)
            minutes = detail['duration']
            detail['time'] = time.strftime('%H:%M')
            detail['message'] = format_markdown(detail['message'])
            data['details'].append(detail)
        time += datetime.timedelta(minutes=minutes)
        data['details'].append(dict(
            time=time.strftime('%H:%M'), message='<p>Ende</p>',
            responsible=''))
        # Commitments
        data['commitments'] = []
        for commitment in self.context.commitments:
            data['commitments'].append(self.get_json(commitment))
        # Attachments
        data['attachments'] = bool(self.context.attachments)
        if self.context.day >= datetime.datetime.now():
            data['type'] = 'AGENDA'
        else:
            data['type'] = 'PROTOKOLL'
        compiler = pybars.Compiler()
        template = compiler.compile(TEMPLATE)
        html = "".join(template(data))
        pdf = BytesIO()
        xhtml2pdf.pisa.CreatePDF(html, dest=pdf)
        pdf.seek(0)

        output = PdfFileWriter()
        append_pdf(PdfFileReader(pdf, strict=False), output)

        for attachment in self.context.attachments:
            if attachment.mimetype in ('application/pdf',):
                pdf = attachment.data
            else:
                pdf = img2pdf.convert(attachment.data)
            append_pdf(PdfFileReader(BytesIO(pdf), strict=False), output)

        result = BytesIO()
        output.write(result)
        result.seek(0)
        return result
