# encoding=utf-8
from pyramid.view import view_config
from sw.allotmentclub import Event, User, Protocol, Assignment, Member
from ..log import user_data_log, log_with_user
from .base import to_string
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.sql.functions import concat
import sw.allotmentclub.browser.base
import pyramid.threadlocal
import sqlalchemy
import datetime


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
                Event.allday.label('Ganztag'),
                User.username.label('Owner'),
            )
            .select_from(Event)
            .join(User)
            .filter(Event.start.isnot(None))
            .filter(Event.title.isnot(None))
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
                sqlalchemy.false().label('Ganztag'),
                to_string('').label('Owner'),
            )
            .select_from(Protocol)
            .filter(Protocol.day.isnot(None))
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
                sqlalchemy.false().label('Ganztag'),
                to_string('').label('Owner'),
            )
            .select_from(Assignment)
            .filter(Assignment.day.isnot(None))
            .join(Member)
        )

        return query.union(arbeitseinsaetze)


class Query(sw.allotmentclub.browser.base.Query):

    def select(self):
        query = VorstandQuery(self.db, self.user).select().union(
            MitgliederQuery(self.db, self.user).select())
        return query.distinct()


@view_config(route_name='calendar', renderer='json', permission='view')
class CalendarView(sw.allotmentclub.browser.base.TableView):

    query_class = Query


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
