# encoding=utf-8
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy import Date, Table, LargeBinary, Boolean, Text
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


MAX_FILE_SIZE = 1024*1024*10  # 10 MB
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
{appellation_or_organization}<br />
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
        if address_data['organization']:
            address_data['appellation_or_organization'] = (
                address_data['organization']
            )
        else:
            address_data['appellation_or_organization'] = (
                address_data['appellation']
            )
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
    organization = Column(String(100), default='')
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
    note = Column(Text)
    get_post = Column(Boolean, default=True)
    leaving_year = Column(Integer)

    messages = relationship("Message", secondary=members_messages_table)
    attachments = sqlalchemy.orm.relation(
        'MemberAttachment', uselist=True, backref='protocol',
        order_by="MemberAttachment.name", cascade='all,delete')

    passive_allotment_id = Column(
        Integer, ForeignKey('allotment.id'), nullable=True)
    passive_allotment = sqlalchemy.orm.relation(
        'Allotment', uselist=True, backref='passive_members',
        foreign_keys=[passive_allotment_id])

    @property
    def active(self):
        return bool(self.allotments)

    @property
    def assignment_hours(self):
        if self.id in (187, 188):  # Werkstatt, Verein
            return 5.0
        from .browser.base import get_selected_year
        hours = 0.0
        year = get_selected_year()
        for assignmentattendee in self.assignments:
            if assignmentattendee.assignment.accounting_year == year:
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


class MemberAttachment(Object):
    """ Eine Anlage zum Mitglied. """

    member_id = Column(
        Integer, ForeignKey('member.id'), nullable=False)
    name = Column(String(100), default=u'')
    mimetype = Column(String(30), default=u'')
    size = Column(String(20), default=u'')
    data = Column(LargeBinary(MAX_FILE_SIZE))


class SaleHistory(Object):

    seller_id = Column(Integer, nullable=False)
    buyer_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False, default=datetime.date.today)


class Allotment(Object):
    """Die Parzelle."""

    number = Column(Integer, nullable=False)
    member_id = Column(Integer, ForeignKey(Member.id), nullable=False)
    member = sqlalchemy.orm.relation(
        'Member', uselist=False, backref='allotments',
        foreign_keys=[member_id])


class Parcel(Object):
    """Das Flustück."""

    number = Column(Integer, nullable=False)
    leased = Column(Boolean, nullable=False, default=False)
    tap_water = Column(Boolean, nullable=False, default=False)
    allotment_id = Column(Integer, ForeignKey(Allotment.id), nullable=False)
    allotment = sqlalchemy.orm.relation(
        'Allotment', uselist=False, backref='parcels')
    map_mimetype = Column(String(100), default='')
    map_size = Column(String(20), default='')
    map_data = Column(LargeBinary(MAX_FILE_SIZE))


class AccessAuthority(Object):
    """Eine Zugriffssteuerung."""

    viewname = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    user = sqlalchemy.orm.relation('User', uselist=False)


class Event(Object):
    """Ein Termin im Kalender."""

    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    user = sqlalchemy.orm.relation('User', uselist=False)

    category = Column(String, nullable=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    start = Column(DateTime, nullable=True)
    end = Column(DateTime, nullable=True)
    allday = Column(Boolean, nullable=False, default=False)
