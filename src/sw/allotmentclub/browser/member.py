# encoding=utf8
from io import BytesIO
from pyramid.response import FileIter
import pybars
from ..log import user_data_log, log_with_user
from .base import date, string_agg, get_selected_year, format_size
from .base import format_mimetype, parse_date
from .letter import render_pdf
from .protocol import format_markdown
from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sw.allotmentclub import BankingAccount, BookingKind, MEMBERSHIP_FEE
from sw.allotmentclub import Member, Allotment, Parcel, Booking
from sw.allotmentclub import SaleHistory, MemberAttachment
import collections
import datetime
import sw.allotmentclub.browser.base
import sw.allotmentclub.browser.external


class Query(sw.allotmentclub.browser.base.Query):

    data_class = {
        'Nachname': 'expand'
    }
    data_hide = {
        'Vorname': 'phone,tablet',
        'Flurstück': 'phone,tablet',
        'Mobil': 'phone,tablet',
        'Straße': 'phone,tablet',
        'PLZ': 'phone,tablet',
        'Ort': 'phone,tablet',
        'Telefon': 'phone',
        'E-Mail': 'phone',
        'Bungalow': 'phone',
        'Geburtstag': 'phone',
    }
    formatters = {
        'Geburtstag': date,
    }

    join_condition = (Allotment.member_id == Member.id)

    fields = (
        Member.id.label('#'),
        func.coalesce(
            string_agg(Allotment.number), 'n/a').label('Bungalow'),
        func.coalesce(
            string_agg(Parcel.number), 'n/a').label('Flurstück'),
        Member.lastname.label('Nachname'),
        Member.firstname.label('Vorname'),
        Member.street.label('Straße'),
        Member.zip.label('PLZ'),
        Member.city.label('Ort'),
        Member.phone.label('Telefon'),
        Member.mobile.label('Mobil'),
        Member.email.label('E-Mail'),
        Member.birthday.label('Geburtstag'),
    )

    def select(self):
        return (
            self.db.query(*self.fields)
            .select_from(Member)
            .join(Allotment, self.join_condition)
            .join(Parcel)
            .group_by(Member.id)
            .filter(Member.leaving_year.is_(None))
            .filter(Member.organization_id == self.user.organization_id)
        )


class ActiveQuery(Query):

    def select(self):
        return super(ActiveQuery, self).select().filter(
            Allotment.id.isnot(None))


@view_config(route_name='member_list', renderer='json', permission='view')
class MemberListView(sw.allotmentclub.browser.base.TableView):

    query_class = ActiveQuery
    available_actions = [
        dict(url='member_edit', btn_class='btn-success',
             icon='fa fa-pencil', title='Bearbeiten'),
        dict(url='member_attachment', btn_class='btn-success',
             icon='fa fa-list', title='Anlagen'),
        dict(url='become_member_letter', btn_class='btn-success',
             icon='fa fa-print', title='Beitrittserklärung drucken'),
        dict(url='direct_debit_letter', btn_class='btn-success',
             icon='fa fa-print', title='Lastschrift drucken'),
        dict(url='mv_entrance_list', btn_class='btn-success',
             icon='fa fa-print', title='Einlasslisten drucken'),
        dict(url='member_sale', btn_class='btn-success',
             icon='fa fa-money', title='Verkauf'),
        dict(url='member_sale_history', btn_class='btn-success',
             icon='fa fa-money', title='Verkaufhistorie'),
        dict(url='membership_fee', btn_class='btn-danger',
             icon='fa fa-money', title='Mitgliedsbeiträge generieren')]


class PassiveQuery(Query):

    join_condition = (Member.passive_allotment_id == Allotment.id)

    def select(self):
        passive = super(PassiveQuery, self).select().filter(
            Member.passive_allotment_id.isnot(None)
        )
        other = (
            self.db.query(*self.fields)
            .select_from(Member)
            .outerjoin(Allotment, Allotment.member_id == Member.id)
            .outerjoin(Parcel)
            .group_by(Member.id)
            .filter(Member.leaving_year.is_(None))
            .filter(Allotment.member_id.is_(None))
            .filter(Member.passive_allotment_id.is_(None))
            .filter(Member.organization_id == self.user.organization_id)
        )
        return passive.union(other).distinct()


@view_config(route_name='member_list_passive', renderer='json',
             permission='view')
class MemberListPassiveView(MemberListView):

    query_class = PassiveQuery
    available_actions = [
        dict(url='member_add', btn_class='btn-success',
             icon='fa fa-plus', title='Neu'),
        dict(url='member_edit', btn_class='btn-success',
             icon='fa fa-pencil', title='Bearbeiten'),
        dict(url='member_attachment', btn_class='btn-success',
             icon='fa fa-list', title='Anlagen'),
        dict(url='become_member_letter', btn_class='btn-success',
             icon='fa fa-print', title='Beitrittserklärung drucken'),
        dict(url='direct_debit_letter', btn_class='btn-success',
             icon='fa fa-print', title='Lastschrift drucken'),
    ]


class LeasedQuery(Query):

    def select(self):
        return super(LeasedQuery, self).select().filter(
            Parcel.leased.is_(True))


@view_config(route_name='member_list_leased', renderer='json',
             permission='view')
class MemberListLeasedView(MemberListView):

    query_class = LeasedQuery
    available_actions = []


class TapWaterQuery(Query):

    def select(self):
        return super(TapWaterQuery, self).select().filter(
            Parcel.tap_water.is_(True))


@view_config(route_name='member_list_tap_water', renderer='json',
             permission='view')
class MemberListTapWaterView(MemberListView):

    query_class = TapWaterQuery
    available_actions = []


@view_config(route_name='member_edit', renderer='json', permission='view')
class MemberEditView(
        sw.allotmentclub.browser.external.ExternalRecipientEditView):

    title = 'Mitglied bearbeiten'

    @property
    def load_options(self):
        options = super(MemberEditView, self).load_options
        options.update({
            'mobile': {'label': 'Mobil-Telefon'},
            'birthday': {
                'label': 'Geburtstag',
                'css_class': 'datepicker',
            },
            'direct_debit': {'label': 'Lastschrift',
                             'template': 'form_boolean'},
            'direct_debit_account_holder': {
                'label': 'Abweichender Kontoinhaber'},
            'iban': {'label': 'IBAN'},
            'bic': {'label': 'BIC'},
            'direct_debit_date': {
                'label': 'Lastschrift-Datum',
                'css_class': 'datepicker'},
            'get_post': {'label': 'Postversand?', 'template': 'form_boolean'},
            'note': {'label': 'Hinweis', 'template': 'form_markdown'},
        })
        if not self.context.active:
            options.update({
                'passive_allotment_id': {
                    'label': 'Passive Mitgliedschaft',
                    'source': self.allotment_source,
                    'css_class': 'chosen',
                    'required': False
                }
            })
        return options

    @property
    def load_data(self):
        fields = list(super(MemberEditView, self).load_data.items())
        fields.extend([
            ('phone', self.context.phone),
            ('mobile', self.context.mobile),
            ('birthday', date(self.context.birthday)),
            ('direct_debit', self.context.direct_debit),
            ('direct_debit_account_holder',
                self.context.direct_debit_account_holder),
            ('iban', self.context.iban),
            ('bic', self.context.bic),
            ('direct_debit_date', date(self.context.direct_debit_date)),
            ('get_post', self.context.get_post),
        ])
        if not self.context.active:
            fields.append(
                ('passive_allotment_id', self.context.passive_allotment_id)
            )
        fields.append(('note', self.context.note))
        return collections.OrderedDict(fields)

    def save(self, key, value):
        if key in ('direct_debit_date', 'birthday'):
            if value:
                value = parse_date(value).date()
            else:
                value = None
        return super(MemberEditView, self).save(key, value)


@view_config(route_name='member_add', renderer='json', permission='view')
class MemberAddView(MemberEditView):

    def __init__(self, context, request):
        context = Member.create()
        context.commit()
        super(MemberAddView, self).__init__(context, request)
        log_with_user(
            user_data_log.info, self.request.user,
            'Mitglied %s hinzugefügt.', self.context.id)

    @property
    def route_name(self):
        return 'member_edit'


@view_config(route_name='membership_fee', renderer='json', permission='view')
class MembershipFeeView(sw.allotmentclub.browser.base.View):

    def update(self):
        account = (BankingAccount.query()
                   .filter(BankingAccount.number == '1')).one()
        kind = (BookingKind.query()
                .filter(BookingKind.title == 'Mitgliedsbeitrag')).one()
        year = get_selected_year()
        members = {}
        for parcel in Parcel.query().all():
            member = parcel.allotment.member
            if not member:
                continue
            if member.lastname in ['Verein', 'Werkstatt']:
                continue
            if member not in members:
                members[member] = [parcel]
            elif parcel not in members[member]:
                members[member].append(parcel)
        for member, parcels in members.items():
            parcel_numbers = '/'.join(
                sorted(set([str(p.number) for p in parcels])))
            parcel_size = sum(p.size for p in parcels)
            for k, v in sorted(MEMBERSHIP_FEE.items()):
                if parcel_size <= k:
                    fee = v
                    break
            Booking.create(
                banking_account=account,
                purpose=(
                    f'Mitgliedsbeitrag {year} Flurstück {parcel_numbers} '
                    f'({parcel_size}qm)'
                ),
                value=0 - fee,
                accounting_year=year,
                booking_day=datetime.date(int(year), 3, 31),
                member=member,
                kind=kind)


class MemberLetter(sw.allotmentclub.browser.base.AddView):

    def get_pdf(self):
        subject = self.request.params['subject']
        message = format_markdown(self.request.params['message'])
        attachments = self.request.params.get('attachments')
        member = self.context if self.with_address else None
        return render_pdf(member, subject, message, self.request.user,
                          attachments=attachments)


def get_member_form_data(member):
    allotments = member.allotments
    if not allotments:
        allotments = member.passive_allotment
    allotment = '/'.join(str(a.number) for a in allotments)

    data = {'member': [
        {'key': 'Anrede', 'value': member.appellation},
        {'key': 'Titel', 'value': member.title},
        {'key': 'Vorname', 'value': member.firstname},
        {'key': 'Nachname', 'value': member.lastname},
        {'key': 'Bungalownummer', 'value': allotment},
        {'key': 'Strasse', 'value': member.street},
        {'key': 'PLZ', 'value': member.zip},
        {'key': 'Ort', 'value': member.city},
        {'key': 'Telefon', 'value': member.phone},
        {'key': 'Mobiltelefon', 'value': member.mobile},
        {'key': 'E-Mail-Adresse', 'value': member.email},
        {'key': 'Geburtstag', 'value': date(member.birthday)},
        {'key': 'IBAN', 'value': member.iban},
        {'key': 'BIC', 'value': member.bic},
        {'key': 'Name Kreditinstitut', 'value': ''},
    ]}

    for item in data['member']:
        if not item['value']:
            item['value'] = '&nbsp;'
    return data


@view_config(route_name='direct_debit_letter', renderer='json',
             permission='view')
class DirectDebitLetter(sw.allotmentclub.browser.base.PrintBaseView):

    with_address = None
    filename = 'Lastschrift'
    subject = 'Lastschrifteinzugsermächtigung'
    subsubject = 'Gläubiger-ID: <b>DE42ZZZ00000348413</b>'
    intro = ''
    message = """
<table style="font-size: 10pt;">
  <tbody>
    {{#each member}}
    <tr>
      <td style="width: 30%;">{{key}}: </td>
      <td style="width: 70%; height: 25pt;">
        {{{value}}}
        <hr style="margin-top: 0px;" />
      </td>
    </tr>
    {{/each}}
  </tbody>
</table>
<p>
Der Vorstand der Bungalowgemeinschaft Roter See e.V. wird hiermit widerruflich
ab sofort ermächtigt, alle im Zusammenhang mit meiner Mitgliedschaft
bestehenden Forderungen wie z.B. Mitgliedsbeiträge oder Energiekosten mittels
Lastschriftverfahren von meinem Konto einzuziehen.
</p>
<table style="font-size: 10pt;">
  <tbody>
    <tr>
      <td style="width: 20%">&nbsp;<hr/>Datum</td>
      <td style="width: 40%;">&nbsp;<hr/>Ort</td>
      <td style="width: 40%;">&nbsp;<hr/>Unterschrift Kontoinhaber</td>
    </tr>
  </tbody>
</table>"""

    def get_pdf(self):
        subject = self.subject
        compiler = pybars.Compiler()
        template = compiler.compile(self.message)
        data = get_member_form_data(self.context)

        message = "".join(template(data))
        member = self.context if self.with_address else None
        return render_pdf(member, subject, message, self.request.user,
                          subsubject=self.subsubject)


@view_config(route_name='become_member_letter', renderer='json',
             permission='view')
class BecomeMemberLetter(sw.allotmentclub.browser.base.PrintBaseView):

    with_address = None
    subject = 'Beitrittserklärung'
    subsubject = ''
    intro = ''
    filename = 'Beitritt'
    message = """
<table style="font-size: 10pt;">
  <tbody>
    {{#each member}}
    <tr>
      <td style="width: 30%;">{{key}}: </td>
      <td style="width: 70%; height: 25pt;">
        {{{value}}}
        <hr style="margin-top: 0px;" />
      </td>
    </tr>
    {{/each}}
  </tbody>
</table>
<p>
Hiermit erkläre ich meinen Beitritt zum Verein Leuna-Bungalowgemeinschaft
"Roter See" e.V. und erkenne die mir vorgelegte Satzung und die Ordnungen der
Leuna-Bungalowgemeinschaft an.
</p>
<table style="font-size: 10pt;">
  <tbody>
    <tr>
      <td style="width: 20%">&nbsp;<hr/>Datum</td>
      <td style="width: 40%;">&nbsp;<hr/>Ort</td>
      <td style="width: 40%;">&nbsp;<hr/>Unterschrift Kontoinhaber</td>
    </tr>
  </tbody>
</table>"""

    def get_pdf(self):
        subject = self.subject
        compiler = pybars.Compiler()
        template = compiler.compile(self.message)
        data = get_member_form_data(self.context)
        data['member'] = data['member'][:-3]

        message = "".join(template(data))
        member = self.context if self.with_address else None
        return render_pdf(member, subject, message, self.request.user,
                          subsubject=self.subsubject)


@view_config(route_name='member_sale', renderer='json', permission='view')
class MemberSaleView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'Grundstücks-Verkauf'

    @property
    def load_options(self):
        return {
            'buyer_id': {
                'source': self.member_source,
                'label': 'Käufer',
                'css_class': 'chosen'
            },
            'transfer_member_due': {
                'label': 'Mitgliedsbeitrag übernehmen',
                'template': 'form_boolean'
            },
            'transfer_advance_pay_one': {
                'label': 'Abschlag I übernehmen',
                'template': 'form_boolean'
            },
            'transfer_advance_pay_two': {
                'label': 'Abschlag II übernehmen',
                'template': 'form_boolean'
            },
            'transfer_energy_bill': {
                'label': 'Energieabrechnung übernehmen',
                'template': 'form_boolean'
            },
            'transfer_assignment_due': {
                'label': 'Arbeitsstunden übernehmen',
                'template': 'form_boolean'
            }
        }

    @property
    def load_data(self):
        fields = [
            ('buyer_id', self.context.id),
            ('transfer_member_due', False),
            ('transfer_advance_pay_one', False),
            ('transfer_advance_pay_two', False),
            ('transfer_energy_bill', False),
            ('transfer_assignment_due', False)]
        return collections.OrderedDict(fields)

    def save(self, key, value):
        year = get_selected_year()
        if key == 'buyer_id':
            buyer = Member.get(value)
            for allotment in self.context.allotments:
                allotment.member = buyer
            SaleHistory.create(seller_id=self.context.id, buyer_id=buyer.id)
            self.context.leaving_year = year
            Booking.create(
                banking_account_id=2,
                booking_day=datetime.date.today(),
                purpose='Aufnahmebeitrag',
                value=-250000,
                member_id=buyer.id,
                kind_id=13,
                accounting_year=year)
        else:
            sale = (SaleHistory.query()
                    .filter(SaleHistory.date == datetime.date.today())
                    .filter(SaleHistory.seller_id == self.context.id)).one()
            buyer = Member.get(sale.buyer_id)
            query = dict(
                transfer_member_due='Mitgliedsbeitrag {}'.format(year),
                transfer_advance_pay_one='Energieabschlag I',
                transfer_advance_pay_two='Energieabschlag II',
                transfer_energy_bill='Energieabrechnung',
                transfer_assignment_due='Arbeitsstunden {}'.format(year)
            )[key]
            for booking in (
                    Booking.query()
                    .filter(Booking.accounting_year == year)
                    .filter(Booking.purpose.ilike('%{}%'.format(query)))
                    .filter(Booking.member == self.context)).all():
                booking.member = buyer
        return True


@view_config(route_name='mv_entrance_list', renderer='json', permission='view')
class MVEntranceListView(sw.allotmentclub.browser.base.XLSXExporterView):

    filename = 'Einlassliste'
    title = 'Liste Einlass MV'

    def query(self):
        return (
            self.db.query(
                Member.lastname.label('Nachname'),
                Member.firstname.label('Vorname'),
                string_agg(Allotment.number).label('Bungalow'),
                Member.email.label('E-Mail-Adresse'),
                Member.direct_debit.label('Lastschrift'),
                Member.id.label('Unterschrift'),
                Member.id.label('Vollmacht'),
            )
            .select_from(Member)
            .join(Allotment, Member.id == Allotment.member_id)
            .group_by(Member.id)
            .filter(Member.lastname != 'Werkstatt')
            .filter(Member.lastname != 'Verein')
            .order_by(Member.lastname)
        )

    def _data(self, query):
        data = super(MVEntranceListView, self)._data(query)
        for item in data:
            item = list(item)
            item[-1] = item[-2] = ''
            yield item


seller = aliased(Member, name='seller')
buyer = aliased(Member, name='buyer')


class MemberSaleHistoryQuery(sw.allotmentclub.browser.base.Query):

    data_class = {
        'Bungalow': 'expand'
    }
    data_hide = {
        'Käufer': 'phone',
        'Datum': 'phone',
        'Verkäufer': 'phone',
        'Flurstück': 'phone,table',
    }

    def select(self):
        return (
            self.db.query(
                SaleHistory.id.label('#'),
                SaleHistory.date.label('Datum'),
                func.coalesce(
                    string_agg(Allotment.number), 'n/a').label('Bungalow'),
                func.coalesce(
                    string_agg(Parcel.number), 'n/a').label('Flurstück'),
                (seller.lastname + ', ' + seller.firstname).label('Verkäufer'),
                (buyer.lastname + ', ' + buyer.firstname).label('Käufer'),
            )
            .select_from(SaleHistory)
            .join(seller, SaleHistory.seller_id == seller.id)
            .join(buyer, SaleHistory.buyer_id == buyer.id)
            .outerjoin(
                Allotment,
                Allotment.member_id.in_((seller.id, buyer.id))
            )
            .outerjoin(Parcel)
            .group_by(SaleHistory.id, seller.lastname, seller.firstname,
                      buyer.lastname, buyer.firstname)
        )


@view_config(route_name='member_sale_history', renderer='json',
             permission='view')
class MemberSaleHistoryView(sw.allotmentclub.browser.base.TableView):

    query_class = MemberSaleHistoryQuery
    default_order_by = 'date'


class AttachmentQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Größe': format_size,
        'Dateityp': format_mimetype,
    }
    data_class = {
        'Name': 'expand'
    }
    data_hide = {
        'Dateityp': 'phone,tablet',
        'Größe': 'phone,tablet',
    }

    def select(self):
        return (
            self.db.query(
                MemberAttachment.id.label('#'),
                MemberAttachment.name.label('Name'),
                MemberAttachment.mimetype.label('Dateityp'),
                MemberAttachment.size.label('Größe'))
            .select_from(MemberAttachment)
            .filter_by(member_id=self.context.id))


@view_config(route_name='member_attachment', renderer='json',
             permission='view')
class MemberAttachmentsView(sw.allotmentclub.browser.base.TableView):
    """ Liste aller Anlagen."""

    query_class = AttachmentQuery
    default_order_by = 'Name'
    available_actions = [
        dict(url='member_attachment_add', btn_class='btn-success',
             icon='fa fa-plus', title='Neu'),
        dict(url='member_attachment_delete', btn_class='btn-danger',
             icon='glyphicon glyphicon-trash', title='Löschen'),
        dict(url='member_attachment_download', btn_class='btn-success',
             icon='fa fa-download', title='Herunterladen')]


@view_config(route_name='member_attachment_add', renderer='json',
             permission='view')
class MemberAttachmentAddView(sw.allotmentclub.browser.base.AddView):

    model = MemberAttachment

    def parse_file(self):
        file = self.request.params.get('file')
        name = file.filename
        data = file.file
        data.seek(0)
        data = data.read()
        mimetype = file.type
        size = len(data)
        return name, mimetype, size, data

    def __call__(self):
        if not self.form_submit():
            return {'status': 'success', 'data': {}}
        name, mimetype, size, data = self.parse_file()
        attachment = self.model.create(
            name=name, mimetype=mimetype, size=size, data=data,
            member_id=self.context.id)
        attachment.commit()
        log_with_user(user_data_log.info,
                      self.request.user,
                      'hat Anlage %s zu Mitglied %s hinzugefügt.',
                      attachment.id, self.context.id)
        return {'status': 'success'}


@view_config(route_name='member_attachment_download',
             permission='view')
class MemberAttachmentDownloadView(sw.allotmentclub.browser.base.View):

    def __call__(self):
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = self.context.mimetype
        response.content_length = int(self.context.size)
        response.content_disposition = (
            'attachment; filename="{}"'.format(self.context.name))
        response.app_iter = FileIter(BytesIO(self.context.data))
        return response


@view_config(route_name='member_attachment_delete', renderer='json',
             permission='view')
class MemberAttachmentDeleteView(sw.allotmentclub.browser.base.DeleteView):

    model = MemberAttachment

    def log(self):
        if self.deleted is not None:
            deleted = self.context.id
            member = self.context.member_id
            log_with_user(user_data_log.info,
                          self.request.user,
                          'hat Anlage %s von Mitglied %s gelöscht.',
                          deleted, member)
