# encoding=utf-8
from __future__ import unicode_literals
from sqlalchemy import Boolean
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy import Date, Table
from sqlalchemy.orm import relationship, ColumnProperty
from sqlalchemy.orm.interfaces import AttributeExtension
from sqlalchemy.ext.instrumentation import InstrumentationManager
import datetime
import json
import pyramid.threadlocal
import risclog.sqlalchemy.interfaces
import risclog.sqlalchemy.model
import sqlalchemy
import sqlalchemy.orm
import sys
import zope.component


ENGINE_NAME = 'portal'


class InstallValidatorListeners(InstrumentationManager):
    def post_configure_attribute(self, class_, key, inst):
        """Add validators for any attributes that can be validated."""
        prop = inst.prop
        # Only interested in simple columns, not relations
        if isinstance(prop, ColumnProperty) and len(prop.columns) == 1:
            col = prop.columns[0]
            if isinstance(col.type, String) and col.type.length:
                sqlalchemy.event.listen(
                    getattr(class_, key), 'set',
                    LengthValidator(col.type.length), retval=True)
            elif isinstance(col.type, Integer):
                sqlalchemy.event.listen(
                    getattr(class_, key), 'set',
                    IntegerValidator(), retval=True)


class ValidationError(Exception):
    pass


class LengthValidator(AttributeExtension):
    def __init__(self, max_length):
        self.max_length = max_length

    def __call__(self, state, value, oldvalue, initiator):
        if value is None:
            return value
        if value:
            value = str(value)
        if len(value) > self.max_length:
            raise ValidationError(
                "Länge von %d übersteigt erlaubte %d" % (
                    len(value), self.max_length))
        return value


class IntegerValidator(AttributeExtension):

    def __call__(self, state, value, oldvalue, initiator):
        if value is None or isinstance(value, int):
            return value
        try:
            return int(value)
        except Exception:
            raise ValidationError(
                "%s ist keine Zahl." % value)


class ObjectBase(risclog.sqlalchemy.model.ObjectBase):

    _engine_name = ENGINE_NAME
    __sa_instrumentation_manager__ = InstallValidatorListeners
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, nullable=False)

    @classmethod
    def context_factory(cls, *args, **kw):
        result = super(ObjectBase, cls).context_factory(*args, **kw)
        # XXX importing browser here is a dependency in the wrong direction,
        # on the other hand, context_factory is used only by Pyramid
        import sw.allotmentclub.browser.auth
        result.__acl__ = sw.allotmentclub.browser.auth.authorize(
            context=result)
        return result

    @classmethod
    def create(cls, *args, **kw):
        if 'organization_id' not in kw:
            request = pyramid.threadlocal.get_current_request()
            if request and hasattr(request, 'user') and request.user:
                kw['organization_id'] = request.user.organization_id
            elif hasattr(sys, '_called_from_test'):
                kw['organization_id'] = 1
        return super(ObjectBase, cls).create(*args, **kw)

    def commit(self):
        db = zope.component.getUtility(risclog.sqlalchemy.interfaces.IDatabase)
        db.session.flush()


Object = risclog.sqlalchemy.model.declarative_base(
    ObjectBase, class_registry=risclog.sqlalchemy.model.class_registry)
MONEY = Numeric(12, 2)


class Organization(Object):
    """An organization like Leuna-Bungalowsiedlung."""

    organization_id = None
    title = Column(String)


class Log(Object):
    """Container in the database for security relevant incidents."""

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    name = Column(String(16))
    level = Column(String(8))
    created = Column(DateTime)
    msg = Column(String(2000))


ADDRESS = """
{appellation}<br />
{title} {firstname} {lastname}<br />
{street}<br />
{zip} {city}<br />
{country}"""

ADDRESS_CHANGE = {
    188: 187,  # Werkstatt -> Leuna Bungalowgemeinschaft
    82: 108,  # Britta Grimmling -> Andreas Grimmling
}


class PersonMixin(object):

    @property
    def address(self):
        address_data = json.loads(json.dumps(self))
        if self.id in ADDRESS_CHANGE:
            realto = Member.get(ADDRESS_CHANGE[self.id])
            realto_data = json.loads(json.dumps(realto))
            for data in ['street', 'zip', 'city', 'country']:
                address_data[data] = realto_data[data]
        address_data['country'] = (
            '' if address_data['country'] == 'Deutschland'
            else address_data['country'])
        return ADDRESS.format(**address_data)

    @property
    def deflection(self):
        return '' if self.appellation == 'Frau' else 'r'

    @property
    def greeting(self):
        return ('Sehr geehrte{deflection} {appellation} {title} '
                '{lastname},').format(**dict(
                    deflection=self.deflection,
                    appellation=self.appellation,
                    title=self.title,
                    lastname=self.lastname))


members_messages_table = Table(
    'members_messages', Object.metadata,
    Column('member_id', Integer, ForeignKey('member.id')),
    Column('message_id', Integer, ForeignKey('message.id'))
)


class Member(Object, PersonMixin):
    """A member in the club."""

    title = Column(String(20), default=u'')
    appellation = Column(String(20), default=u'')
    firstname = Column(String(50), default=u'')
    lastname = Column(String(50), default=u'')
    street = Column(String(100), default=u'')
    zip = Column(String(6), default=u'')
    city = Column(String(50), default=u'')
    country = Column(String(50), default=u'')
    phone = Column(String(50), default=u'')
    mobile = Column(String(50), default=u'')
    email = Column(String(100), default=u'')
    birthday = Column(Date)
    iban = Column(String(34), default=u'')
    bic = Column(String(11), default=u'')
    direct_debit_account_holder = Column(String(100))
    direct_debit = Column(Boolean)
    direct_debit_date = Column(DateTime)
    get_post = Column(Boolean, default=True)
    leaving_year = Column(Integer)

    messages = relationship("Message", secondary=members_messages_table)

    @property
    def assignment_hours(self):
        if self.id in (187, 188):  # Werkstatt, Verein
            return 5.0
        from .browser.base import get_selected_year
        hours = 0.0
        for assignmentattendee in self.assignments:
            if assignmentattendee.assignment.day.year == get_selected_year():
                hours += assignmentattendee.hours
        return hours

    def bill_assignment_hours(self):
        from .account import Booking, BookingKind
        missing_hours = 5 - self.assignment_hours
        from .browser.base import get_selected_year
        year = get_selected_year()
        kind = (BookingKind.query()
                .filter(BookingKind.shorttitle == 'NARB')).one()
        if missing_hours > 0:
            Booking.find_or_create(
                banking_account_id=2,
                booking_day=datetime.date(int(year), 10, 31),
                purpose='fehlende %s Arbeitsstunden %s' % (
                    missing_hours, year),
                value=0 - int(missing_hours * 10) * 10000,
                accounting_year=year,
                member=self,
                kind=kind)


class SaleHistory(Object):

    seller_id = Column(Integer, nullable=False)
    buyer_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False, default=datetime.date.today)


class Allotment(Object):
    """Die Parzelle."""

    number = Column(Integer, nullable=False)
    member_id = Column(Integer, ForeignKey(Member.id), nullable=False)
    member = sqlalchemy.orm.relation(
        'Member', uselist=False, backref='allotments')


class Parcel(Object):
    """Das Flustück."""

    number = Column(Integer, nullable=False)
    leased = Column(Boolean, nullable=False, default=False)
    tap_water = Column(Boolean, nullable=False, default=False)
    allotment_id = Column(Integer, ForeignKey(Allotment.id), nullable=False)
    allotment = sqlalchemy.orm.relation(
        'Allotment', uselist=False, backref='parcels')


class AccessAuthority(Object):
    """Eine Zugriffssteuerung."""

    viewname = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    user = sqlalchemy.orm.relation('User', uselist=False)


class DashboardData(Object):
    """Daten für das Dashboard."""

    id = None
    date = Column(DateTime, nullable=False,
                  server_default=sqlalchemy.func.now(), primary_key=True)
    luefterstufe = Column(Integer, nullable=False)
    luefter_percent = Column(Integer, nullable=False)
    luefter_abluft_feuchte = Column(Integer, nullable=False)
    luefter_aussenluft = Column(Numeric(3, 1), nullable=False)
    luefter_zuluft = Column(Numeric(3, 1), nullable=False)
    luefter_fortluft = Column(Numeric(3, 1), nullable=False)
    luefter_abluft = Column(Numeric(3, 1), nullable=False)

    rotersee_temp_out_battery = Column(Integer, nullable=True)
    rotersee_rain_battery = Column(Integer, nullable=True)
    rotersee_out_temp = Column(Numeric(3, 1),  nullable=True)
    rotersee_in_temp = Column(Numeric(3, 1),  nullable=True)
    rotersee_out_humi = Column(Integer, nullable=True)
    rotersee_in_humi = Column(Integer, nullable=True)
    rotersee_in_co2 = Column(Integer, nullable=True)
    rotersee_rain = Column(Integer, nullable=True)
    rotersee_rain_1 = Column(Integer, nullable=True)
    rotersee_rain_24 = Column(Integer, nullable=True)
    rotersee_out_temp_trend = Column(String,  nullable=True)

    wachtelberg_temp_out_battery = Column(Integer, nullable=True)
    wachtelberg_temp_in_battery = Column(Integer, nullable=True)
    wachtelberg_rain_battery = Column(Integer, nullable=True)
    wachtelberg_wind_battery = Column(Integer, nullable=True)
    wachtelberg_out_temp = Column(Numeric(3, 1),  nullable=True)
    wachtelberg_in_temp = Column(Numeric(3, 1),  nullable=True)
    wachtelberg_out_humi = Column(Integer, nullable=True)
    wachtelberg_in_humi = Column(Integer, nullable=True)
    wachtelberg_in_co2 = Column(Integer, nullable=True)
    wachtelberg_rain = Column(Integer, nullable=True)
    wachtelberg_rain_1 = Column(Integer, nullable=True)
    wachtelberg_rain_24 = Column(Integer, nullable=True)
    wachtelberg_wind_strength = Column(Integer, nullable=True)
    wachtelberg_wind_angle = Column(Integer, nullable=True)
    wachtelberg_out_temp_trend = Column(String,  nullable=True)
