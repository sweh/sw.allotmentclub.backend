# encoding=utf8
from ..log import user_data_log, log_with_user
from .base import date, string_agg, get_selected_year
from .letter import render_pdf
from .protocol import format_markdown
from pyramid.response import FileIter
from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sw.allotmentclub import BankingAccount, BookingKind, VALUE_PER_MEMBER
from sw.allotmentclub import Member, Allotment, Parcel, Booking
from sw.allotmentclub import SaleHistory
import collections
import datetime
import dateutil.parser
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

    def select(self):
        return (
            self.db.query(
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
            .select_from(Member)
            .outerjoin(Allotment)
            .outerjoin(Parcel)
            .group_by(Member.id, Parcel.leased)
            .filter(Member.leaving_year.is_(None))
        )


@view_config(route_name='member_list', renderer='json', permission='view')
class MemberListView(sw.allotmentclub.browser.base.TableView):

    query_class = Query
    default_order_by = 'lastname'
    available_actions = [
        dict(url='direct_debit_letter', btn_class='btn-success',
             icon='fa fa-print', title='Lastschrift drucken'),
        dict(url='become_member_letter', btn_class='btn-success',
             icon='fa fa-print', title='Beitrittserklärung drucken'),
        dict(url='mv_entrance_list', btn_class='btn-success',
             icon='fa fa-print', title='Einlasslisten drucken'),
        dict(url='member_sale', btn_class='btn-success',
             icon='fa fa-money', title='Verkauf'),
        dict(url='member_sale_history', btn_class='btn-success',
             icon='fa fa-money', title='Verkaufhistorie'),
        dict(url='member_add', btn_class='btn-success',
             icon='fa fa-plus', title='Neu'),
        dict(url='member_edit', btn_class='btn-success',
             icon='fa fa-pencil', title='Bearbeiten'),
        dict(url='membership_fee', btn_class='btn-danger',
             icon='fa fa-money', title='Mitgliedsbeiträge generieren')]


class LeasedQuery(Query):

    def select(self):
        return super(LeasedQuery, self).select().filter(
            Parcel.leased.is_(True))


@view_config(route_name='member_list_leased', renderer='json',
             permission='view')
class MemberListLeasedView(MemberListView):

    query_class = LeasedQuery


class TapWaterQuery(Query):

    def select(self):
        return super(TapWaterQuery, self).select().filter(
            Parcel.tap_water.is_(True))


@view_config(route_name='member_list_tap_water', renderer='json',
             permission='view')
class MemberListTapWaterView(MemberListView):

    query_class = TapWaterQuery


@view_config(route_name='member_edit', renderer='json', permission='view')
class MemberEditView(
        sw.allotmentclub.browser.external.ExternalRecipientEditView):

    title = 'Mitglied bearbeiten'

    @property
    def load_options(self):
        options = super(MemberEditView, self).load_options
        options.update({
            'phone': {'label': 'Telefon'},
            'mobile': {'label': 'Mobil-Telefon'},
            'birthday': {'label': 'Geburtstag'},
            'direct_debit': {'label': 'Lastschrift',
                             'template': 'form_boolean'},
            'direct_debit_account_holder': {
                'label': 'Abweichender Kontoinhaber'},
            'iban': {'label': 'IBAN'},
            'bic': {'label': 'BIC'},
            'direct_debit_date': {
                'label': 'Lastschrift-Datum',
                'css_class': 'datetimepicker'},
            'get_post': {'label': 'Postversand?', 'template': 'form_boolean'},
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
        return collections.OrderedDict(fields)

    def save(self, key, value):
        if key in ('direct_debit_date', 'birthday'):
            if value:
                value = dateutil.parser.parse(value).date()
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
        members = []
        for parcel in Parcel.query().all():
            member = parcel.allotment.member
            if not member:
                continue
            if member.lastname in ['Verein', 'Werkstatt']:
                continue
            members.append(member)
        for member in set(members):
            Booking.create(
                banking_account=account,
                purpose='Mitgliedsbeitrag %s' % get_selected_year(),
                value=0 - VALUE_PER_MEMBER,
                accounting_year=get_selected_year(),
                booking_day=datetime.date(int(get_selected_year()), 3, 31),
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


@view_config(route_name='direct_debit_letter', renderer='json',
             permission='view')
class DirectDebitLetter(sw.allotmentclub.browser.base.View):

    with_address = None
    subject = 'Lastschrifteinzugsermächtigung'
    subsubject = 'Gläubiger-ID: <b>DE42ZZZ00000348413</b>'
    intro = ''
    message = """
<table style="font-size: 10pt;">
  <tbody>
    <tr>
      <td style="width: 30%;">&nbsp;<hr/>Vorname</td>
      <td style="width: 40%">&nbsp;<hr/>Nachname</td>
      <td style="width: 30%;">&nbsp;<hr/>Bungalownummer</td>
    </tr>
    <tr>
      <td style="width: 30%;">&nbsp;<hr/>Straße</td>
      <td style="width: 40%">&nbsp;<hr/>PLZ</td>
      <td style="width: 30%;">&nbsp;<hr/>Ort</td>
    </tr>
    <tr>
      <td style="width: 30%;">&nbsp;<hr/>Telefon</td>
      <td style="width: 40%">&nbsp;<hr/>Mobil</td>
      <td style="width: 30%;">&nbsp;<hr/>E-Mail-Adresse</td>
    </tr>
  </tbody>
</table>

<p>
Der Vorstand der Bungalowgemeinschaft Roter See e.V. wird hiermit widerruflich
ab sofort ermächtigt, die fälligen Mitgliedsbeiträge sowie die
Energiekostenabschläge und den Endabrechnungsbetrag für den Energieverbrauch
mittels Lastschriftverfahren von meinem Konto einzuziehen.
</p>

<table style="font-size: 10pt;">
  <tbody>
    <tr>
      <td style="width: 40%;">&nbsp;<hr/>IBAN</td>
      <td style="width: 20%">&nbsp;<hr/>BIC</td>
      <td style="width: 40%;">&nbsp;<hr/>Name Kreditinstit</td>
    </tr>
    <tr>
      <td style="width: 40%;">&nbsp;<hr/>Ort</td>
      <td style="width: 20%">&nbsp;<hr/>Datum</td>
      <td style="width: 40%;">&nbsp;<hr/>Unterschrift Kontoinhaber</td>
    </tr>
  </tbody>
</table>"""

    def update(self):
        pdf = self.get_pdf()
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = 'application/pdf'
        response.content_disposition = 'attachment; filename=Lastschrift.pdf'
        response.app_iter = FileIter(pdf)
        self.result = response

    def get_pdf(self):
        subject = self.subject
        message = self.intro + self.message
        message = format_markdown(message)
        member = self.context if self.with_address else None
        return render_pdf(member, subject, message, self.request.user,
                          subsubject=self.subsubject)


@view_config(route_name='become_member_letter', renderer='json',
             permission='view')
class BecomeMemberLetter(sw.allotmentclub.browser.base.View):

    with_address = None
    subject = 'Beitrittserklärung'
    intro = ''
    message = """
<table style="font-size: 10pt;">
  <tbody>
    <tr>
      <td style="width: 30%;">&nbsp;<hr/>Vorname</td>
      <td style="width: 40%">&nbsp;<hr/>Nachname</td>
      <td style="width: 30%;">&nbsp;<hr/>Bungalownummer</td>
    </tr>
    <tr>
      <td style="width: 30%;">&nbsp;<hr/>Straße</td>
      <td style="width: 40%">&nbsp;<hr/>PLZ</td>
      <td style="width: 30%;">&nbsp;<hr/>Ort</td>
    </tr>
    <tr>
      <td style="width: 30%;">&nbsp;<hr/>Telefon</td>
      <td style="width: 40%">&nbsp;<hr/>Mobil</td>
      <td style="width: 30%;">&nbsp;<hr/>E-Mail-Adresse</td>
    </tr>
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
      <td style="width: 40%;">&nbsp;<hr/>Ort</td>
      <td style="width: 20%">&nbsp;<hr/>Datum</td>
      <td style="width: 40%;">&nbsp;<hr/>Unterschrift</td>
    </tr>
  </tbody>
</table>"""

    def update(self):
        pdf = self.get_pdf()
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = 'application/pdf'
        response.content_disposition = 'attachment; filename=Beitritt.pdf'
        response.app_iter = FileIter(pdf)
        self.result = response

    def get_pdf(self):
        subject = self.subject
        message = self.intro + self.message
        message = format_markdown(message)
        member = self.context if self.with_address else None
        return render_pdf(member, subject, message, self.request.user)


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
            .join(Allotment)
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
            .outerjoin(Allotment)
            .outerjoin(Parcel)
            .group_by(SaleHistory.id, seller.lastname, seller.firstname,
                      buyer.lastname, buyer.firstname)
        )


@view_config(route_name='member_sale_history', renderer='json',
             permission='view')
class MemberSaleHistoryView(sw.allotmentclub.browser.base.TableView):

    query_class = MemberSaleHistoryQuery
    default_order_by = 'date'
