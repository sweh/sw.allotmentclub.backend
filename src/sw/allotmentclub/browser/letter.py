# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from sw.allotmentclub import Member
from io import BytesIO
import email.utils
import pkg_resources
import pybars
import pyramid.threadlocal
import pyramid_mailer
import pyramid_mailer.message
import re
import xhtml2pdf.pisa
import unicodedata

from reportlab import rl_config
rl_config.invariant = True


LOGO = pkg_resources.resource_stream(
    'sw.allotmentclub.browser', 'logo_letter.txt').read().decode('utf-8')

TEMPLATE_HEADER = """
<html lang="de">
<head>
<meta charset="utf-8"/>
<style>
    body { font-size: {{font_size}}; }
    #content { font-style: italic; }
    .txt-color-red { font-color: red; }
    {{{styles}}}
</style>
</head>

<body>
    <div id="header_content" style="font-size: 9pt;">
      <h1 style="font-family: Helvetica; color: #1f496d;
                 font-size: 16pt; margin: 0px; padding: 0px;">
        Leuna&mdash;Bungalowgemeinschaft Roter See e.V.</h1>
      Postfach 4023<br />
      06233 Leuna<br />
      vorstand@roter-see.de
    </div>
    <div id="logo">
      <img src="{{logo}}" />
    </div>
"""

TEMPLATE_FOOTER = """
    <table><tbody><tr><td>
      {{#if from_}}
      <p>Mit freundlichen Grüßen<br />Im Auftrag des Vorstandes</p>
      {{#if signature}}
        <img style="height: 25pt" src="{{signature}}" />
      {{else}}
        <br />
      {{/if}}
      <p style="font-style: italic;">
        {{{from_}}}
      </p>
      {{/if}}
    </td>
    <td style="vertical-align: bottom; text-align: right;">
      {{#if attachments}}
      <p style="font-size: {{font_size}}; padding-right: 10pt;">
        <span style="font-weight: bold;">Anlagen</span>
        {{#each attachments}}
          <br />{{title}}
        {{/each}}
      </p>
      {{/if}}
    </td></td></tbody></table>
    <div id="footer_content" style="font-size: 9pt">
      <table style="margin: 0px; padding: 0px;">
        <tr>
          <td style="width: 35%; text-align: left;">
          Amtsgericht Stendal VR 46284</td>
          <td style="width: 30%; text-align: center;"></td>
          <td style="width: 35%; text-align: right;">
          Vorsitzender: Hartmut Schlöffel</td>
        </tr>
      </table>
      <hr style="margin: 0px; padding: 0px;" />
      <table style="margin: 0px; padding: 0px; margin-top: 3pt;">
        <tr>
          <td style="width: 35%; text-align: left;">Saalesparkasse</td>
          <td style="width: 30%; text-align: center;">BIC: NOLADE21HAL</td>
          <td style="width: 35%; text-align: right;">
          IBAN: DE71 8005 3762 3440 0001 67</td>
        </tr>
      </table>
    </div>
</body>
</html>"""

PDF_TEMPLATE = TEMPLATE_HEADER + """
    {{#if address}}
    <p style="font-size: 7pt; text-decoration: underline;
              padding-bottom: 7pt;">
      Leuna&mdash;Bungalowgemeinschaft Roter See e.V.&nbsp;&nbsp;Postfach 4023
      &nbsp;&nbsp;06233 Leuna
    </p>
    <div style="font-size: 11pt; line-height: 11pt; padding-top: 13pt;">
      {{{address}}}
    </div>
    {{/if}}
    {{#if address}}
    <p style="text-align: right; width: 100%; padding-top: 30pt;
              margin-top: 0px;">
      {{city}}, den {{date}}</p>
    {{/if}}
    {{#if subject}}
    <h2 style="font-size: {{font_size}};">
      {{{subject}}}
      {{#if subsubject}}
      <br />
      <span style="font-weight: normal">{{{subsubject}}}</span><br />
      {{/if}}
    </h2>
    {{/if}}
    <div id="content">
      {{{content}}}
    </div>
""" + TEMPLATE_FOOTER

PDF_STYLES = """
    @page {
        size: a4 portrait;
        @frame header_frame {
            -pdf-frame-content: header_content;
            left: 50pt; width: 412pt; top: 50pt; height: 80pt;
        }
        @frame logo_frame {
            -pdf-frame-content: logo;
            left: 462pt; width: 00pt; top: 50px; height: 80pt;
        }
        @frame content_frame {
            left: 50pt; width: 512pt; top: 145pt; height: 600pt;
        }
        @frame footer_frame {
            -pdf-frame-content: footer_content;
            left: 50pt; width: 512pt; top: 752pt; height: 40pt;
        }
    }
"""

MAIL_TEMPLATE = TEMPLATE_HEADER + """
    <p style="text-align: right; width: 100%; padding-top: 30pt;
              margin-top: 0px;">
      {{city}}, den {{date}}</p>
    <div id="content">
      {{{content}}}
    </div>
""" + TEMPLATE_FOOTER

MAIL_STYLES = """
    #header_content { display: block; padding-top: 10pt; width: 80% }
    #logo { display: block; position: absolute; top: 8pt; right: 8pt; }
    #logo img { height: 50pt; }
    #footer_content { display: block; width: 100%; }
    #content { display: block; padding: 0pt 10pt 0pt 0pt; }
    table { padding: 0pt 10pt 20pt 0pt; font-size: 12pt; font-style: italic; }
    #footer_content table { width: 100%; font-size: 9pt; }
"""

compiler = pybars.Compiler()
pdf_template = compiler.compile(PDF_TEMPLATE)
mail_template = compiler.compile(MAIL_TEMPLATE)


def render_pdf(
        to, subject, content, user, date=None,
        subsubject=None, attachments=None, font_size='12pt', force_from=False):
    if date is None:
        date = datetime.now()
    if isinstance(to, Member):
        to = to.address
    if not to and not force_from:
        from_ = None
    else:
        from_ = '{} {} ({})'.format(user.vorname, user.nachname, user.position)
    data = dict(
        styles=PDF_STYLES,
        subject=subject, subsubject=subsubject, content=content, from_=from_,
        city=user.ort if user else None,
        signature=user.signature if user else None,
        date=date.strftime('%d.%m.%Y') if date else None,
        address=to if to else None, logo=LOGO,
        attachments=attachments, font_size=font_size)
    html = "".join(pdf_template(data))
    pdf = BytesIO()
    xhtml2pdf.pisa.CreatePDF(src=html, dest=pdf, encoding='utf-8')
    pdf.seek(0)
    return pdf


def send_mail(to, subject, content, user, date=None, attachments=[],
              font_size='12pt', self_cc=False):
    if date is None:
        date = datetime.now()
    from_ = '{} {} ({})'.format(user.vorname, user.nachname, user.position)
    data = dict(
        styles=MAIL_STYLES, content=content, from_=from_, city=user.ort,
        signature=user.signature, date=date.strftime('%d.%m.%Y'), address=True,
        font_size=font_size, logo=LOGO)
    html = "".join(mail_template(data))
    text = """
{}

Mit freundlichen Grüßen,
Im Auftrag des Vorstandes

{}""".format(content, from_)

    text = re.sub('<[^<]+?>', '', text)
    msg_tag = email.utils.make_msgid()
    msg = pyramid_mailer.message.Message(
        subject=subject,
        recipients=[to],
        cc=['vorstand@roter-see.de'] if self_cc else None,
        sender=('Vorstand Leuna-Bungalowgemeinschaft Roter See '
                '<vorstand@roter-see.de>'),
        extra_headers={'X-PM-Tag': msg_tag},
        body=text,
        html=html)
    for attachment in attachments:
        filename = attachment.filename
        try:
            # Prevent tuple exception in repoze.sendmail if filename contains
            # non-ascii characters
            filename = (unicodedata
                        .normalize('NFKD', filename)
                        .encode('ASCII', 'ignore')
                        .decode())
        except Exception:
            pass
        msg.attach(pyramid_mailer.message.Attachment(
            filename, attachment.mimetype, attachment.data))
    mailer = pyramid_mailer.get_mailer(
        pyramid.threadlocal.get_current_request())
    mailer.send(msg)
    return msg_tag
