# encoding=utf-8
from pyramid.view import view_config
from sw.allotmentclub import Event, User, Protocol, Assignment, Member
from sw.allotmentclub import SEPASammler, BookingKind
from ..log import user_data_log, log_with_user
from .base import to_string, get_selected_year, date, date_time
from .letter import render_pdf
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.sql.functions import concat
import pybars
import sw.allotmentclub.browser.base
import pyramid.threadlocal
import sqlalchemy
import zope.component
import risclog.sqlalchemy.interfaces


class BaseQuery(sw.allotmentclub.browser.base.Query):

    def select(self):
        return (
            self.db.query(
                Event.id.label('#'),
                Event.category.label('Liste'),
                Event.title.label('Titel'),
                Event.description.label('Beschreibung'),
                Event.start.label('Start'),
                Event.end.label('Ende'),
                to_string('Termin').label('Typ'),
                Event.allday.label('Ganztag'),
                User.username.label('Owner'),
            )
            .select_from(Event)
            .join(User)
            .filter(Event.start.isnot(None))
            .filter(Event.title.isnot(None))
            .filter(Event.organization_id == self.user.organization_id)
        )


class VorstandQuery(BaseQuery):

    def select(self):
        query = super(VorstandQuery, self).select()
        query = query.filter(Event.category == 'Vorstand')

        sitzungen = (
            self.db.query(
                sqlalchemy.null().label('#'),
                to_string('Vorstand').label('Liste'),
                Protocol.title.label('Titel'),
                Protocol.location.label('Beschreibung'),
                Protocol.day.label('Start'),
                (
                    Protocol.day + sqlalchemy.func.cast(
                        concat(3, ' HOURS'), INTERVAL
                    )
                ).label('Ende'),
                to_string('Vorstandssitzung').label('Typ'),
                sqlalchemy.false().label('Ganztag'),
                to_string('').label('Owner'),
            )
            .select_from(Protocol)
            .filter(Protocol.day.isnot(None))
            .filter(Protocol.organization_id == self.user.organization_id)
        )

        return query.union(sitzungen)


class MitgliederQuery(BaseQuery):

    def select(self):
        query = super(MitgliederQuery, self).select()
        query = query.filter(Event.category == 'Mitglieder')

        arbeitseinsaetze = (
            self.db.query(
                sqlalchemy.null().label('#'),
                to_string('Mitglieder').label('Liste'),
                Assignment.purpose.label('Titel'),
                to_string(Member.lastname).concat(', ').concat(
                    Member.firstname).label('Beschreibung'),
                Assignment.day.label('Start'),
                (
                    Assignment.day + sqlalchemy.func.cast(
                        concat(2.5, ' HOURS'), INTERVAL
                    )
                ).label('Ende'),
                to_string('Arbeitseinsatz').label('Typ'),
                sqlalchemy.false().label('Ganztag'),
                to_string('').label('Owner'),
            )
            .select_from(Assignment)
            .filter(Assignment.day.isnot(None))
            .filter(Assignment.organization_id == self.user.organization_id)
            .join(Member)
        )

        lastschriften = (
            self.db.query(
                sqlalchemy.null().label('#'),
                to_string('Mitglieder').label('Liste'),
                to_string('Einzug ').concat(BookingKind.title).label('Titel'),
                to_string(
                    'Bitte sorgen Sie für ausreichend Deckung auf Ihrem '
                    'Konto').label('Beschreibung'),
                SEPASammler.booking_day.label('Start'),
                SEPASammler.booking_day.label('Ende'),
                to_string('Lastschrift').label('Typ'),
                sqlalchemy.true().label('Ganztag'),
                to_string('').label('Owner'),
            )
            .select_from(SEPASammler)
            .filter(SEPASammler.booking_day.isnot(None))
            .filter(SEPASammler.organization_id == self.user.organization_id)
            .join(BookingKind)
        )

        return query.union(arbeitseinsaetze).union(lastschriften)


class BirthdayQuery(sw.allotmentclub.browser.base.Query):

    def select(self, year=None):
        if not year:
            year = get_selected_year()
        return (
            self.db.query(
                sqlalchemy.null().label('#'),
                to_string('Geburtstage').label('Liste'),
                to_string(Member.lastname).concat(', ').concat(
                    Member.firstname).label('Titel'),
                (
                    to_string(year - sqlalchemy.cast(
                        sqlalchemy.func.extract('year', Member.birthday),
                        sqlalchemy.INTEGER
                    )).concat('. Geburtstag')
                ).label('Beschreibung'),
                sqlalchemy.cast((
                    to_string(year)
                    .concat('-')
                    .concat(
                        sqlalchemy.func.extract('month', Member.birthday)
                    )
                    .concat('-')
                    .concat(
                        sqlalchemy.func.extract('day', Member.birthday)
                    )
                ), sqlalchemy.DATE).label('Start'),
                sqlalchemy.null().label('Ende'),
                to_string('Geburtstag').label('Typ'),
                sqlalchemy.true().label('Ganztag'),
                to_string('').label('Owner'),
            )
            .select_from(Member)
            .filter(Member.birthday.isnot(None))
            .filter(Member.leaving_year.is_(None))
            .filter(Member.organization_id == self.user.organization_id)
        )


class Query(sw.allotmentclub.browser.base.Query):

    def select(self):
        query = VorstandQuery(self.db, self.user).select().union(
            MitgliederQuery(self.db, self.user).select())
        year = get_selected_year()
        for year in [year-1, year, year+1]:
            query = query.union(BirthdayQuery(self.db, self.user).select(year))
        return query.distinct()


@view_config(route_name='calendar', renderer='json', permission='view')
class CalendarView(sw.allotmentclub.browser.base.TableView):

    query_class = Query

    available_actions = [
        dict(url='infobrief_print', btn_class='btn-success',
             icon='fa fa-print', title='Termine Info-Brief')]


@view_config(route_name='infobrief_print', permission='view')
class InfobriefPrintView(sw.allotmentclub.browser.base.PrintBaseView):

    filename = 'Termine'
    subject = 'Termine'
    message = """
<h2>Lastschrifteinzüge</h2>
<table style="font-size: 10pt;">
  <tbody>
    {{#each Lastschrift}}
    <tr>
      <td style="width: 40%;">{{date}}</td>
      <td style="width: 60%">{{title}}</td>
    </tr>
    {{/each}}
  </tbody>
</table>

<h2>wichtige Termine</h2>
<table style="font-size: 10pt;">
  <tbody>
    {{#each Termin}}
    <tr>
      <td style="width: 40%;">{{date}}</td>
      <td style="width: 60%">{{title}}</td>
    </tr>
    {{/each}}
  </tbody>
</table>

<h2>Geplante Arbeitseinsätze</h2>
<table style="font-size: 10pt;">
  <tbody>
    {{#each Arbeitseinsatz}}
    <tr>
      <td style="width: 40%;">{{date}}</td>
      <td style="width: 60%">{{title}}</td>
    </tr>
    {{/each}}
  </tbody>
</table>"""

    def get_pdf(self):
        year = get_selected_year()
        subject = self.subject + f' {year}'
        compiler = pybars.Compiler()
        template = compiler.compile(self.message)

        db = zope.component.getUtility(
            risclog.sqlalchemy.interfaces.IDatabase
        )
        query = MitgliederQuery(db, self.request.user)
        events = []
        for event in query.select():
            if event[4].year != year:
                continue
            events.append(
                dict(
                    date=event[4],
                    title=event[2],
                    type_=event[-3],
                    allday=event[-2]
                )
            )
        data = {
            'Lastschrift': [],
            'Arbeitseinsatz': [],
            'Termin': [],
        }
        for event in sorted(events, key=lambda x: x['date']):
            datum = (
                date(event['date']) if event['allday']
                else date_time(event['date'])
            )
            data[event['type_']].append(dict(
                date=datum, title=event['title']
            ))

        message = "".join(template(data))
        return render_pdf(None, subject, message, self.request.user)


@view_config(route_name='calendar_event_add', renderer='json',
             permission='view')
class CalendarEventAddView(sw.allotmentclub.browser.base.View):

    model = Event

    def __call__(self):
        data = self.request.json
        event = Event.create(user=self.request.user)
        event.allday = data['allday']
        if event.allday:
            offset = 10
        else:
            offset = 16
        event.start = data['start'][0:offset]
        if data['end']:
            event.end = data['end'][0:offset]
        event.category = data['category']
        event.title = data['title']
        event.description = data['description']
        event.commit()

        log_with_user(
            user_data_log.info,
            self.request.user,
            f'Termin {event.id} ({event.title}) in Kalender eingefügt.'
        )
        return event.id

    def log(self):
        if self.deleted is None:
            return
        if self.context.user != pyramid.threadlocal.get_current_request().user:
            raise RuntimeError('Not allowed to delete event')
        log_with_user(
            user_data_log.info,
            self.request.user,
            f'Termin {self.context.id} ({self.context.title}) aus Kalender '
            f'gelöscht.'
        )


@view_config(route_name='calendar_event_delete', renderer='json',
             permission='view')
class CalendarEventDeleteView(sw.allotmentclub.browser.base.DeleteView):

    model = Event

    def log(self):
        if self.deleted is None:
            return
        if self.context.user != pyramid.threadlocal.get_current_request().user:
            raise RuntimeError('Not allowed to delete event')
        log_with_user(
            user_data_log.info,
            self.request.user,
            f'Termin {self.context.id} ({self.context.title}) aus Kalender '
            f'gelöscht.'
        )
