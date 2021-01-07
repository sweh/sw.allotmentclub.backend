# encoding=utf8
from __future__ import unicode_literals
from ..log import user_data_log, log_with_user
from .base import date, get_selected_year, value_to_int, boolean, date_time
from .base import format_eur_with_color, format_eur, format_date, to_string
from .base import string_agg, parse_date
from .mail import append_pdf, render_pdf, format_markdown
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import BytesIO
from pyramid.response import FileIter
from pyramid.view import view_config
from sqlalchemy.sql import func
from sw.allotmentclub import Booking, Member, Allotment, GrundsteuerB, Abwasser
from sw.allotmentclub import BookingKind, SEPASammler, SEPASammlerEntry
from sw.allotmentclub import Budget, VALUE_PER_MEMBER
import collections
import datetime
import pybars
import re
import sqlalchemy
import sw.allotmentclub.browser.base

BOOKING_FUTURE = datetime.datetime.now() + datetime.timedelta(days=61)


def AccountDetailFactory(request):
    account_id, account_type = request.matchdict['id'].split('-')
    context = getattr(sw.allotmentclub.account,
                      account_type).get(account_id)
    context.__acl__ = sw.allotmentclub.browser.auth.DEFAULT_ACL
    return context


class Query(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Betrag': format_eur_with_color,
    }

    css_classes = {
        'Betrag': 'right nowrap',
        'Datum': 'nowrap',
        'Zugeordnet': 'nowrap',
    }

    data_class = {
        'Buchungsinfo': 'expand'
    }
    data_hide = {
        'Datum': 'phone',
        'Betrag': 'phone',
        'Zugeordnet': 'phone,tablet',
    }

    def select(self):
        from sqlalchemy.sql.expression import false
        return (
            self.db.query(
                Booking.id.label('#'),
                Booking.booking_day.label('Datum'),
                (to_string(Booking.booking_text).concat('<br />')
                 .concat(to_string(Booking.purpose)).concat('<br />')
                 .concat(to_string(Booking.recipient)).label('Buchungsinfo')),
                Booking.value.label('Betrag'),
                (to_string(Member.lastname).concat(' (')
                 .concat(func.coalesce(string_agg(Allotment.number), 'n/a'))
                 .concat(')').label('Zugeordnet')),
                BookingKind.shorttitle.label('Typ'),
            )
            .select_from(Booking)
            .outerjoin(Member)
            .outerjoin(Allotment, Allotment.member_id == Member.id)
            .outerjoin(BookingKind)
            .group_by(Booking.id, Member.lastname, BookingKind.shorttitle)
            .filter(Booking.banking_account == self.context)
            .filter(Booking.is_splitted == false())
            .filter(Booking.accounting_year == get_selected_year()))


@view_config(route_name='booking_list', renderer='json',
             permission='view')
class BookingListView(sw.allotmentclub.browser.base.TableView):

    query_class = Query
    default_order_by = 'booking_day'
    year_selection = True
    available_actions = [
        dict(url='map_booking', btn_class='btn-success',
             icon='fa fa-hand-o-right', title='Zuordnen'),
        dict(url='split_booking', btn_class='btn-success',
             icon='fa fa-scissors', title='Aufteilen')
    ]


@view_config(route_name='split_booking', renderer='json',
             permission='view')
class SplitBookingView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'Buchung aufteilen'

    @property
    def load_options(self):
        return {
            'new_value': {
                'label': 'Teilen bei Betrag',
                'required': True
            }
        }

    @property
    def load_data(self):
        fields = [
            ('new_value', '')
        ]
        return collections.OrderedDict(fields)

    def fail(self, message):
        self.result['status'] = 'error'
        self.result['msg'] = message

    def update(self):
        try:
            json = self.request.json
        except ValueError:
            json = None
        if json:
            new_value = value_to_int(json['new_value'])
            status = self.context.split(new_value)
            if isinstance(status, str):
                self.fail(status)
                return
            log_with_user(
                user_data_log.info, self.request.user,
                'Buchung %s bei %s aufgeteilt.',
                self.context.id, format_eur(new_value))
            self.result = {'status': 'success'}
        else:
            self.result = self.get_result()


@view_config(route_name='map_booking', renderer='json',
             permission='view')
class MapBookingView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'Buchung einem Mitglied zuweisen'

    @property
    def load_options(self):
        result = {
            'member_id': {
                'source': self.member_source,
                'label': 'Mitglied',
                'css_class': 'chosen',
                'required': False
            },
            'kind_id': {
                'source': self.booking_kind_source,
                'label': 'Typ',
                'css_class': 'chosen',
                'required': False
            },
            'accounting_year': {
                'source': self.accounting_year_source,
                'label': 'Jahr',
                'css_class': 'chosen',
                'required': True
            }
        }
        return result

    @property
    def load_data(self):
        fields = [
            ('member_id', self.context.member_id),
            ('kind_id', self.context.kind_id),
            ('accounting_year', self.context.accounting_year)]
        return collections.OrderedDict(fields)


def get_balance(value, request=None):
    from sqlalchemy.sql.expression import true, false, case
    import zope.component
    import risclog.sqlalchemy
    member = Member.get(value)
    db = zope.component.getUtility(risclog.sqlalchemy.interfaces.IDatabase)
    bookings = (
        db.query(func.sum(Booking.value))
        .join(Member)
        .filter(Booking.member == member)
        .filter(Booking.is_splitted == false())
        .filter(Booking.booking_day <= BOOKING_FUTURE)
        .filter(Booking.accounting_year == get_selected_year()))
    sepa = (
        db.query(func.sum(
            case([
                (
                    SEPASammler.is_ueberweisung == true(),
                    0 - SEPASammlerEntry.value
                )],
                else_=SEPASammlerEntry.value,
            ).label('Betrag'),
        ))
        .join(Member)
        .join(SEPASammler)
        .filter(SEPASammlerEntry.member == member)
        .filter(SEPASammler.booking_day <= BOOKING_FUTURE)
        .filter(SEPASammler.accounting_year == get_selected_year()))
    booking_sum = bookings.one()[0]
    sepa_sum = sepa.one()[0]
    booking_sum = 0 if booking_sum is None else booking_sum
    sepa_sum = 0 if sepa_sum is None else sepa_sum
    return format_eur_with_color(booking_sum + sepa_sum)


class MemberAccountQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Konto': get_balance,
    }

    css_classes = {
        'Konto': 'right nowrap',
    }

    data_class = {
        'Mitglied': 'expand'
    }
    data_hide = {
        'Konto': 'phone',
    }

    def select(self):
        return (
            self.db.query(
                Member.id.label('#'),
                (to_string(Member.lastname).concat(', ')
                 .concat(to_string(Member.firstname)).label('Mitglied')),
                Member.id.label('Konto')
            )
            .select_from(Member)
            .filter(sqlalchemy.or_(
                Member.leaving_year.is_(None),
                Member.leaving_year >= get_selected_year())))


@view_config(route_name='member_account_list', renderer='json',
             permission='view')
class MemberAccountListView(sw.allotmentclub.browser.base.TableView):

    query_class = MemberAccountQuery
    default_order_by = 'member.id'
    year_selection = True
    available_actions = [
        dict(url='member_account_detail_list', btn_class='btn-success',
             icon='fa fa-list', title='Buchungen'),
    ]


class MemberAccountDetailQuery(sw.allotmentclub.browser.base.Query):

    disable_global_organization_filter = True

    formatters = {
        'Betrag': format_eur_with_color,
        'Datum': date,
        'RS': boolean
    }

    css_classes = {
        'Betrag': 'right nowrap',
    }

    data_class = {
        'Datum': 'expand'
    }
    data_hide = {
        'Betrag': 'phone',
        'Typ': 'phone, tablet',
    }

    def select(self):
        from sqlalchemy.sql.expression import true, false, case
        bookings = (
            self.db.query(
                to_string(Booking.id).concat('-Booking').label('#'),
                Booking.booking_day.label('Datum'),
                BookingKind.title.label('Typ'),
                Booking.value.label('Betrag'),
                Booking.ignore_in_reporting.label('RS')
            )
            .select_from(Booking)
            .outerjoin(BookingKind)
            .join(Member)
            .filter(Booking.is_splitted == false())
            .filter(Booking.accounting_year == get_selected_year())
            .filter(Booking.booking_day <= BOOKING_FUTURE)
            .filter(Booking.organization_id == self.user.organization_id)
            .filter(Booking.member == self.context))
        sepa = (
            self.db.query(
                (to_string(SEPASammlerEntry.id)
                 .concat('-SEPASammlerEntry').label('#')),
                SEPASammler.booking_day.label('Datum'),
                BookingKind.title.label('Typ'),
                case([
                    (
                        SEPASammler.is_ueberweisung == true(),
                        0 - SEPASammlerEntry.value
                    )],
                    else_=SEPASammlerEntry.value,
                ).label('Betrag'),
                SEPASammlerEntry.ignore_in_reporting.label('RS')
            )
            .select_from(SEPASammler)
            .join(SEPASammlerEntry)
            .outerjoin(BookingKind)
            .join(Member)
            .filter(SEPASammler.accounting_year == get_selected_year())
            .filter(SEPASammler.booking_day <= BOOKING_FUTURE)
            .filter(SEPASammler.organization_id == self.user.organization_id)
            .filter(SEPASammlerEntry.member == self.context))
        return bookings.union(sepa)


@view_config(route_name='member_account_detail_list', renderer='json',
             permission='view')
class MemberAccountDetailListView(sw.allotmentclub.browser.base.TableView):

    query_class = MemberAccountDetailQuery
    year_selection = True
    available_actions = [
        dict(url='member_account_detail_switch_ir',
             btn_class='btn-danger',
             icon='fa fa-check-square-o ', title='Reporting-Status ändern'),
    ]


@view_config(route_name='member_account_detail_switch_ir', renderer='json',
             permission='view')
class MemberAccountDetailSwitchRSView(sw.allotmentclub.browser.base.View):

    def update(self):
        self.context.ignore_in_reporting = not self.context.ignore_in_reporting
        self.result = {'status': 'success',
                       'message': 'Reporting-Status geändert.'}


def get_budget_raw(value, request=None, year=None):
    year = year if year else get_selected_year()
    kind = BookingKind.get(value)
    return [
        Budget.query()
        .filter(Budget.booking_kind == kind)
        .filter(Budget.accounting_year == year)
        .one()
    ]


def get_budget_sum(value, request=None, year=None):
    year = year if year else get_selected_year()
    kind = BookingKind.get(value)
    if kind.shorttitle == 'ENAB':
        kind = BookingKind.query().filter_by(shorttitle='ENAN').one()
        query = (
            Booking.query()
            .filter(Booking.kind == kind)
            .filter(Booking.accounting_year == year)
        )
        return 0 - sum(b.value for b in query)
    return sum(b.value for b in get_budget_raw(value, request, year))


def get_budget(value, request=None, year=None):
    return format_eur_with_color(get_budget_sum(value, request, year))


def get_incoming_raw(value, request=None, year=None):
    from sqlalchemy.sql.expression import false
    year = year if year else get_selected_year()
    kind = BookingKind.get(value)
    query = (
        Booking.query()
        .join(Member)
        .filter(Booking.kind == kind)
        .filter(Booking.accounting_year == year)
        .filter(Booking.ignore_in_reporting == false())
        .filter(Booking.is_splitted == false())
        .filter(Booking.banking_account_id == 1)
        .filter(Booking.booking_text != 'SAMMEL-LS-EINZUG')
        .filter(~Booking.purpose.like('%ANZAHL 00000%'))
    )
    sammler = (
        SEPASammlerEntry.query()
        .join(SEPASammler)
        .join(Member)
        .filter(SEPASammler.kind == kind)
        .filter(SEPASammlerEntry.ignore_in_reporting == false())
        .filter(SEPASammler.accounting_year == year)
    )
    result = query.all() + sammler.all()
    if kind.shorttitle == 'ENAB':
        result += (
            get_incoming_raw(
                BookingKind.query().filter_by(shorttitle='ENA1').one().id,
                request, year
            ) +
            get_incoming_raw(
                BookingKind.query().filter_by(shorttitle='ENA2').one().id,
                request, year
            )
        )
    return result


def get_incoming_sum(value, request=None, year=None):
    result = 0
    for item in get_incoming_raw(value, request, year):
        value = item.value
        if hasattr(item, 'sepasammler'):
            if item.sepasammler.is_ueberweisung:
                value = 0 - value
        result += value
    return result


def get_incoming(value, request=None, year=None):
    return format_eur_with_color(get_incoming_sum(value, request, year))


def get_incoming_pre_year(value, request=None):
    return get_incoming(value, request, get_selected_year()-1)


def get_sum(value, request=None):
    budget = get_budget_sum(value, request)
    actual = get_incoming_sum(value, request)

    return format_eur_with_color(actual - budget)


class BankingAccountQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Vorjahr': get_incoming_pre_year,
        'Budget': get_budget,
        'Ist': get_incoming,
        'Differenz': get_sum,
    }

    css_classes = {
        'Vorjahr': 'right nowrap',
        'Budget': 'right nowrap',
        'Ist': 'right nowrap',
        'Differenz': 'right nowrap',
    }

    data_class = {
        'Kategorie': 'expand'
    }
    data_hide = {
        'Vorjahr': 'phone',
        'Budget': 'phone',
        'Ist': 'phone',
        'Differenz': 'phone,tablet'
    }

    def select(self):
        return (
            self.db.query(
                BookingKind.id.label('#'),
                BookingKind.title.label('Kategorie'),
                BookingKind.id.label('Vorjahr'),
                BookingKind.id.label('Budget'),
                BookingKind.id.label('Ist'),
                BookingKind.id.label('Differenz')
            )
            .select_from(BookingKind)
            .filter(~BookingKind.shorttitle.in_(('ENA1', 'ENA2', 'ENAN')))
        )


@view_config(route_name='banking_account_list', renderer='json',
             permission='view')
class BankingAccountListView(sw.allotmentclub.browser.base.TableView):

    query_class = BankingAccountQuery
    year_selection = True
    available_actions = [
        dict(url='banking_account_list_detail', btn_class='btn-success',
             icon='fa fa-list', title='Positionen'),
        dict(url='banking_account_list_report', btn_class='btn-success',
             icon='fa fa-print', title='Report')
    ]


@view_config(route_name='banking_account_list_detail', renderer='json',
             permission='view')
class BankingAccountListDetailView(sw.allotmentclub.browser.base.TableView):

    def __call__(self):
        incoming = get_incoming_raw(self.context.id, self.request)
        columns = [
            {'name': name, 'css_class': 'hide' if id == 0 else ''}
            for id, name in enumerate(
                ['#', 'Betrag', 'Mitglied', 'Buchungstext', 'Datum'])]
        result = []
        for obj in incoming:
            value = obj.value
            if not hasattr(obj, 'booking_text'):
                if obj.sepasammler.is_ueberweisung:
                    type_ = 'Sammel-Überweisung'
                    value = 0 - value
                else:
                    type_ = 'Sammel-Lastschrift'
                text = (
                    f'{type_} {obj.sepasammler.kind.title} '
                    f'{obj.sepasammler.pmtinfid}'
                )
            else:
                text = obj.purpose
            new_line = [
                {'value': obj.id, 'css_class': 'hide'},
                {'value': format_eur_with_color(value, self.request)},
                {'value': '{}, {} ({})'.format(
                    obj.member.lastname, obj.member.firstname,
                    (obj.member.allotments[0].number
                        if obj.member.allotments else ''))},
                {'value': text},
                {'value': format_date(
                    obj.booking_day if hasattr(obj, 'booking_day')
                    else obj.sepasammler.booking_day)},
            ]
            result.append(new_line)
        data = {'data': result,
                'header': columns,
                'actions': [],
                'records': len(result)}
        return {'status': 'success', 'data': data}


@view_config(route_name='banking_account_list_report', renderer='json',
             permission='view')
class BankingAccountListReportView(sw.allotmentclub.browser.base.View):

    hbs_page = """
<h3>{{title}}</h3>
<table style="border: 1px solid black;">
  <tr style="font-style: normal; font-size: 8pt;">
    <th style="width: 10%; {{{header_style}}}">Betrag</th>
    <th style="width: 23%; {{{header_style}}}">Mitglied</th>
    <th style="width: 58%; {{{header_style}}}">Buchungstext</th>
    <th style="width: 9%; {{{header_style}}}">Datum</th>
  </tr>
  {{#each content}}
    <tr>
      {{#each this}}
      <td style="border: 1px solid black;
                 padding: 2px 2px -1px 2px;
                 {{#unless @index}} text-align: right; {{/unless}}
                 font-style: normal;
                 font-size: 8pt;">{{{this}}}</td>
      {{/each}}
    </tr>
  {{/each}}
  <tr style="font-style: normal; font-size: 8pt;">
    <th style="width: 10%; {{{header_style}}}">SUMME</th>
    <th colspan="3" style="{{{header_style}}}">{{summe}}</th>
  </tr>
</table>
"""

    def update(self):
        output = PdfFileWriter()
        compiler = pybars.Compiler()
        compiled_page = compiler.compile(self.hbs_page)
        cleanr = re.compile('<.*?>')

        for kind in BookingKind.query():
            data = BankingAccountListDetailView(kind, self.request)()['data']
            table_content = []
            for item in data['data']:
                table_content.append(
                    [(re.sub(cleanr, '', d['value'])
                      if d['value'] else '&nbsp;') for d in item[1:5]])
            table_content = sorted(
                table_content,
                key=lambda x: (x[1], x[0], x[2]))  # sort by name
            sum_ = sum(float(
                i[0].replace(' €', '').replace('.', '').replace(',', '.'))
                for i in table_content)
            sum_ = int(sum_ * 10000)

            body = format_markdown(compiled_page(dict(
                title='{} {}'.format(
                    kind.title, get_selected_year()),
                content=table_content,
                summe=format_eur(sum_),
                header_style=("border: 1px solid black; "
                              "padding: 2px 2px -1px 2px;"))))
            output = self.add_page(body, output)
        result = BytesIO()
        output.write(result)
        result.seek(0)
        response = self.request.response
        response.set_cookie('fileDownload', value='true')
        response.content_type = 'application/pdf'
        response.content_disposition = 'attachment; filename=Report 2018.pdf'
        response.app_iter = FileIter(result)
        self.result = response

    def add_page(self, body, output):
        pdf = render_pdf(None, None, body, None, date=None, force_from=False)
        pdf = PdfFileReader(pdf, strict=False)
        append_pdf(pdf, output)
        return output


class SEPASammlerQuery(sw.allotmentclub.browser.base.Query):

    data_class = {
        'Art': 'expand'
    }
    data_hide = {
        'Sparkassen-ID': 'phone,tablet',
        'Datum': 'phone,tablet',
    }

    def select(self):
        from sqlalchemy.sql.expression import case, literal, true
        return (
            self.db.query(
                SEPASammler.id.label('#'),
                BookingKind.title.label('Art'),
                SEPASammler.booking_day.label('Datum'),
                SEPASammler.pmtinfid.label('Sparkassen-ID'),
                case(
                    [
                        (
                            SEPASammler.is_ueberweisung == true(),
                            literal('Sammelüberweisung')
                        ),
                    ],
                    else_=literal('Sammellastschrift')
                ).label('Typ'),
            )
            .select_from(SEPASammler)
            .outerjoin(BookingKind)
            .filter(SEPASammler.accounting_year == get_selected_year()))


@view_config(route_name='sepa_sammler_list', renderer='json',
             permission='view')
class SEPASammlerListView(sw.allotmentclub.browser.base.TableView):

    query_class = SEPASammlerQuery
    year_selection = True
    start_year = 2015
    available_actions = [
        dict(url='sepa_sammler_add', btn_class='btn-success',
             icon='fa fa-plus', title='Neue Sammellastschrift'),
        dict(url='sepa_ueberweisung_add', btn_class='btn-success',
             icon='fa fa-plus', title='Neue Sammelüberweisung'),
        dict(url='sepa_sammler_edit', btn_class='btn-success',
             icon='fa fa-pencil', title='Bearbeiten'),
        dict(url='sepa_sammler_entry_list', btn_class='btn-success',
             icon='fa fa-list', title='Positionen'),
        dict(url='sepa_sammler_update', btn_class='btn-success',
             icon='fa fa-list', title='autom. Befüllen'),
        dict(url='sepa_sammler_export', btn_class='btn-success',
             icon='fa fa-bank', title='Export Sparkasse'),
    ]


@view_config(route_name='sepa_sammler_update', renderer='json',
             permission='view')
class SEPASammlerUpdateView(sw.allotmentclub.browser.base.View):

    def advancepay(self):
        values = (
            Booking.query()
            .filter(Booking.accounting_year == self.context.accounting_year)
            .filter(Booking.kind == self.context.kind).all())
        for value in values:
            if value.value < 0:
                if value.member and value.member.direct_debit:
                    SEPASammlerEntry().find_or_create(
                        sepasammler=self.context,
                        value=0 - value.value,
                        member=value.member)

    def energieabrechnung(self):
        values = (
            Booking.query()
            .filter(Booking.accounting_year == self.context.accounting_year)
            .filter(Booking.kind == self.context.kind)).all()
        if self.context.is_ueberweisung:
            values = [v for v in values if v.value > 0]
        else:
            values = [v for v in values if v.value <= 0]
        for value in values:
            if value.member.direct_debit:
                SEPASammlerEntry().find_or_create(
                    sepasammler=self.context,
                    value=(
                        value.value
                        if self.context.is_ueberweisung
                        else 0 - value.value
                    ),
                    member=value.member)

    def grundsteuerb(self):
        values = GrundsteuerB.query().all()
        for value in values:
            member = value.parcel.allotment.member
            if member.direct_debit:
                SEPASammlerEntry().find_or_create(
                    sepasammler=self.context,
                    value=value.value,
                    member=value.parcel.allotment.member)

    def abwasser(self):
        values = Abwasser.query().all()
        for value in values:
            member = value.parcel.allotment.member
            if member.direct_debit:
                SEPASammlerEntry().find_or_create(
                    sepasammler=self.context,
                    value=value.value,
                    member=member)

    @property
    def active_members(self):
        return super(SEPASammlerUpdateView, self).active_members.filter(
            Member.direct_debit.is_(True)
        )

    def arbeitsstunden(self):
        for member in self.active_members.all():
            bookings = (
                Booking.query()
                .filter(
                    Booking.accounting_year == self.context.accounting_year)
                .filter(Booking.kind == self.context.kind)
                .filter(Booking.member == member).all())
            value = 0
            for booking in bookings:
                value -= booking.value
            if value:
                SEPASammlerEntry().find_or_create(
                    sepasammler=self.context,
                    value=value,
                    member=member)

    def mitgliedsbeitrag(self):
        for member in self.active_members.all():
            SEPASammlerEntry().find_or_create(
                sepasammler=self.context,
                value=VALUE_PER_MEMBER,
                member=member)

    def update(self):
        if not self.context.kind:
            self.result = {'status': 'error',
                           'message': 'Art muss gesetzt sein.'}
            return
        for entry in (
                SEPASammlerEntry.query()
                .filter(SEPASammlerEntry.sepasammler == self.context).all()):
            entry.delete()
        if self.context.kind.shorttitle in ('ENA1', 'ENA2'):
            self.advancepay()
        elif self.context.kind.shorttitle == 'ENAB':
            self.energieabrechnung()
        elif self.context.kind.shorttitle == 'GRUB':
            self.grundsteuerb()
        elif self.context.kind.shorttitle == 'ABWA':
            self.abwasser()
        elif self.context.kind.shorttitle == 'NARB':
            self.arbeitsstunden()
        elif self.context.kind.shorttitle == 'BEIT':
            self.mitgliedsbeitrag()
        else:
            self.result = {
                'status': 'error',
                'message': '{} nicht unterstützt'.format(
                    self.context.kind.title)
            }
            return
        self.result = {
            'status': 'success',
            'message': 'SEPASammler {} berechnet.'.format(
                self.context.kind.title)}


@view_config(route_name='sepa_sammler_edit', renderer='json',
             permission='view')
class SEPASammlerEditView(sw.allotmentclub.browser.base.EditJSFormView):

    title = 'SEPA Sammler bearbeiten'

    @property
    def load_options(self):
        return {
            'kind_id': {
                'label': 'Art',
                'css_class': 'chosen',
                'required': True,
                'source': self.booking_kind_source,
            },
            'booking_day': {
                'label': 'Datum',
                'css_class': 'datetimepicker',
            },
            'pmtinfid': {
                'label': 'Sparkassen-ID',
            }
        }

    @property
    def booking_kind_source(self):
        result = super(SEPASammlerEditView, self).booking_kind_source
        if self.context.is_ueberweisung:
            return [r for r in result if r['title'] == 'Energieabrechnung']
        return result

    @property
    def load_data(self):
        fields = [
            ('kind_id', self.context.kind_id),
            ('booking_day', date_time(self.context.booking_day)),
            ('pmtinfid', self.context.pmtinfid),
        ]
        return collections.OrderedDict(fields)

    def save(self, key, value):
        if key == 'booking_day' and value:
            value = parse_date(value).date()
        return super(SEPASammlerEditView, self).save(key, value)

    def update(self):
        super(SEPASammlerEditView, self).update()
        if self.context.booking_day:
            if isinstance(self.context.booking_day, datetime.date):
                self.context.accounting_year = self.context.booking_day.year
            else:
                self.context.accounting_year = (
                    parse_date(self.context.booking_day).year)


@view_config(route_name='sepa_sammler_add', renderer='json',
             permission='view')
class SEPASammlerAddView(SEPASammlerEditView):

    def __init__(self, context, request):
        context = SEPASammler.create()
        context.commit()
        super(SEPASammlerAddView, self).__init__(context, request)
        self.log()

    def log(self):
        log_with_user(
            user_data_log.info, self.request.user,
            'SEPA Sammler %s hinzugefügt.', self.context.id)

    @property
    def route_name(self):
        return 'sepa_sammler_edit'


@view_config(route_name='sepa_ueberweisung_add', renderer='json',
             permission='view')
class SEPAUeberweisungAddView(SEPASammlerAddView):

    def log(self):
        self.context.is_ueberweisung = True
        log_with_user(
            user_data_log.info, self.request.user,
            'SEPA Überweisung %s hinzugefügt.', self.context.id)


@view_config(route_name='sepa_sammler_export', renderer='json',
             permission='view')
class SEPASammlerExportView(sw.allotmentclub.browser.base.SEPAExporterView):

    @property
    def filename(self):
        return '{} {}'.format(
            self.context.kind.title, self.context.accounting_year)

    @property
    def subject(self):
        return self.filename

    @property
    def values(self):
        return sorted(self.context.entries, key=lambda x: x.member.lastname)

    def get_member(self, value):
        return value.member

    def get_to_pay(self, value):
        return value.value

    @property
    def creation_date(self):
        return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    @property
    def booking_day(self):
        return self.context.booking_day.strftime('%Y-%m-%d')


class SEPASammlerEntryQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Betrag': format_eur,
        'Ignorieren': boolean,
    }

    data_class = {
        'Zugeordnet': 'expand'
    }

    data_hide = {
        'Ignorieren': 'phone,tablet',
        'Betrag': 'phone'
    }

    def select(self):
        return (
            self.db.query(
                SEPASammlerEntry.id.label('#'),
                (to_string(Member.lastname).concat(', ').concat(
                 to_string(Member.firstname).concat(' (')
                 .concat(func.coalesce(string_agg(Allotment.number), 'n/a'))
                 .concat(')'))).label('Zugeordnet'),
                SEPASammlerEntry.value.label('Betrag'),
                SEPASammlerEntry.ignore_in_reporting.label('Ignorieren')
            )
            .select_from(SEPASammlerEntry)
            .filter(SEPASammlerEntry.sepasammler == self.context)
            .join(Member)
            .outerjoin(Allotment, Allotment.member_id == Member.id)
            .group_by(SEPASammlerEntry.id, Member.lastname, Member.firstname))


@view_config(route_name='sepa_sammler_entry_list', renderer='json',
             permission='view')
class SEPASammlerEntryListView(sw.allotmentclub.browser.base.TableView):

    query_class = SEPASammlerEntryQuery
    year_selection = False


def account_holder(id, request=None):
    member = Member.get(id)
    result = member.direct_debit_account_holder or (
        '%s, %s' % (member.lastname, member.firstname))
    return '%s (%s)' % (
        result, '/'.join(str(a.number) for a in member.allotments))


class SEPADirectDebitQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Mitglied': account_holder,
    }
    data_class = {
        'Mitglied': 'expand'
    }
    data_hide = {
        'IBAN': 'phone',
        'BIC': 'phone,tablet',
        'Datum': 'phone,tablet',
    }

    def select(self):
        from sqlalchemy.sql.expression import true
        return (
            self.db.query(
                Member.id.label('#'),
                Member.id.label('Mitglied'),
                Member.iban.label('IBAN'),
                Member.bic.label('BIC'),
                Member.direct_debit_date.label('Datum'),
            )
            .select_from(Member)
            .join(Allotment, Allotment.member_id == Member.id)
            .group_by(Member.id)
            .filter(Member.direct_debit == true())
        )


@view_config(route_name='sepa_direct_debit', renderer='json',
             permission='view')
class SEPADirectDebitListView(sw.allotmentclub.browser.base.TableView):

    query_class = SEPADirectDebitQuery
