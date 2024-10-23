# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .model import Object
from .base import format_kwh, format_eur
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, sql
from sw.allotmentclub.account import Booking, BookingKind, BankingAccount
import datetime
import sqlalchemy.orm

THRESHOLD = 100000.0


class ElectricMeter(Object):
    """ Der Stromzähler."""

    allotment_id = Column(Integer, ForeignKey('allotment.id'), nullable=False)
    allotment = sqlalchemy.orm.relation(
        'Allotment', uselist=False, backref='electric_meters')
    energy_values = sqlalchemy.orm.relation(
        'EnergyValue', uselist=True, backref='electric_meter',
        cascade="delete")
    number = Column(String)
    electric_power = Column(Boolean, default=sql.false())
    disconnected = Column(Boolean, default=sql.false())
    comment = Column(String)
    replaced_by_id = Column(
        Integer, ForeignKey('electricmeter.id'), nullable=True)
    replaced_by = sqlalchemy.orm.relation('ElectricMeter', uselist=False)
    discount_to_id = Column(
        Integer, ForeignKey('member.id'), nullable=True)
    discount_to = sqlalchemy.orm.relation('Member', uselist=False)

    @classmethod
    def by_number(cls, number):
        return cls.query().filter(cls.number == str(number)).one_or_none()

    def get_value(self, year):
        for value in self.energy_values:
            if value.year == year:
                return value

    def get_last_value(self, exclude=None):
        if (len(self.energy_values) == 1):
            return self.energy_values[0]
        start = min([v.year for v in self.energy_values])
        last_value = self.get_value(start)
        for value in self.energy_values:
            if value is exclude:
                continue
            if ((getattr(value, 'value', 0) or 0) >
                    (getattr(last_value, 'value', 0) or 0)):
                last_value = value
        return last_value

    def replace(self, old_value, new_number, new_value):
        year = datetime.datetime.now().year
        new = ElectricMeter()
        new.allotment = self.allotment
        new.number = new_number
        new.electric_power = self.electric_power
        self.replaced_by = new
        new.discount_to = self.discount_to
        new.organization_id = self.organization_id

        last_value = self.get_last_value()
        if last_value.value < old_value:
            value = EnergyValue.create(
                electric_meter=self, year=year, value=old_value,
                organization_id=self.organization_id)
            value.update_member()
            value.update_usage()
            self.energy_values.append(value)

        value = EnergyValue.create(
            electric_meter=new, year=year-1, value=new_value,
            organization_id=self.organization_id)
        value.update_member()
        value.advance_pay = value.fee = value.price = value.usage = 0
        value.whole_price = value.to_pay = 0
        value.discounted = True
        new.energy_values.append(value)
        self.disconnected = True
        return new


class EnergyValue(Object):
    """ Der Zählerstand."""

    electric_meter_id = Column(Integer, ForeignKey(ElectricMeter.id),
                               nullable=False)
    year = Column(Integer)
    value = Column(Integer)
    estimated_value = Column(Boolean, default=sql.false())
    member_id = Column(Integer, ForeignKey('member.id'), nullable=True)
    member = sqlalchemy.orm.relation(
        'Member', uselist=False, backref='energy_values')
    usage = Column(Integer, nullable=True)
    price = Column(Integer, nullable=True)
    fee = Column(Integer, nullable=True)
    whole_price = Column(Integer, nullable=True)
    to_pay = Column(Integer, nullable=True)
    advance_pay = Column(Integer, nullable=True)
    discounted = Column(Boolean, nullable=True)

    def update_member(self):
        if not self.member:
            if self.electric_meter.discount_to:
                self.member = self.electric_meter.discount_to
            else:
                self.member = self.electric_meter.allotment.member

    def update_usage(self):
        self.usage = self._usage

    def update_data(self):
        from sw.allotmentclub.browser.account import value_to_int
        from sw.allotmentclub.browser.base import format_eur
        if self.discounted:
            return
        self.price = self._price
        self.fee = self._fee
        self.whole_price = self._whole_price
        self.to_pay = self._to_pay
        # if self._advance_pay >= THRESHOLD:
        #     self.advance_pay = int(self._advance_pay)
        # else:
        #     self.advance_pay = 0
        self.advance_pay = 0
        purpose = 'Energieabrechnung'
        month = 8
        day = 31
        try:
            kind = (BookingKind.query()
                    .filter(BookingKind.title == purpose).one())
        except sqlalchemy.orm.exc.NoResultFound:
            pass
        else:
            account = (BankingAccount.query()
                       .filter(BankingAccount.number == '3').one())
            booking = Booking.find_or_create(
                banking_account=account,
                purpose='{} für Zähler {}'.format(
                    purpose, self.electric_meter.number),
                accounting_year=self.year,
                booking_day=datetime.date(self.year, month, day),
                member=self.member,
                kind=kind)
            booking.value = 0 - value_to_int(format_eur(self.to_pay)[:-2])
        if self.member.lastname in ['Verein', 'Werkstatt']:
            return
        return
        for purpose, month, day in [('Energieabschlag I', 3, 31),
                                    ('Energieabschlag II', 6, 30)]:
            try:
                kind = (BookingKind.query()
                        .filter(BookingKind.title == purpose).one())
            except sqlalchemy.orm.exc.NoResultFound:
                continue
            account = (BankingAccount.query()
                       .filter(BankingAccount.number == '3').one())
            booking = Booking.find_or_create(
                banking_account=account,
                purpose='{} für Zähler {}'.format(
                    purpose, self.electric_meter.number),
                accounting_year=self.year+1,
                booking_day=datetime.date(self.year+1, month, day),
                member=self.member,
                kind=kind)
            booking.value = 0 - value_to_int(format_eur(self.advance_pay)[:-2])

    @property
    def _usage(self):
        before = self.electric_meter.get_last_value(self)
        if before is None or self.value is None or before.value is None:
            return 0
        return self.value - before.value

    @property
    def _price(self):
        try:
            price = EnergyPrice.query().filter(
                EnergyPrice.year == self.year).one()
        except Exception:
            return 0
        if not price.price:
            return 0
        return self.usage * price.price

    @property
    def _fee(self):
        try:
            price = EnergyPrice.query().filter(
                EnergyPrice.year == self.year).one()
        except Exception:
            return 0
        if self.electric_meter.disconnected:
            return 0
        if not price.power_fee or not price.normal_fee:
            return 0
        if self.electric_meter.electric_power:
            return price.power_fee
        return price.normal_fee

    @property
    def _whole_price(self):
        return (round(self.fee/10000, 2) + round(self.price/10000, 2)) * 10000

    @property
    def advance_pay_last_year(self):
        # XXX Use real value from booking
        last_value = self.electric_meter.get_value(self.year-1)
        if last_value:
            advance_pay_last_year = last_value.advance_pay
            advance_pay_last_year = int(
                round(advance_pay_last_year / 10000.0, 2) * 10000
            )
        else:
            advance_pay_last_year = 0
        return advance_pay_last_year * 2

    @property
    def _to_pay(self):
        return self.whole_price - self.advance_pay_last_year

    @property
    def _advance_pay(self):
        # Calculate the advance payment for the next year
        return int(self.whole_price / 300) * 100


class EnergyPrice(Object):
    """ Der Preis einer kWh. """

    year = Column(Integer)
    value = Column(Integer)  # Stand Hauptzähler zur Abrechnung
    bill = Column(Integer)  # Abrechnung Energieanbieter in Eur
    usage_hauptzaehler = Column(Integer)  # Verbrauch Hauptzaehler
    usage_members = Column(Integer)  # Verbrauch Mitglieder
    leakage_current = Column(Integer)  # Verluststrom
    price = Column(Integer)  # Preis in MicroCent pro kWh
    normal_fee = Column(Integer)  # Gebühr normaler Zähler in MicroCent
    power_fee = Column(Integer)  # Gebühr Kraftstrom-Zähler in MicroCent


def format_iban(iban):
    if not iban or len(iban) < 10:
        return iban
    return 'X' * 10 + iban[10:]


def get_energyvalue_mail_data(member, year):
    for value in (EnergyValue.query()
                  .filter(EnergyValue.year == year)
                  .filter(EnergyValue.member == member)).all():
        price = (
            EnergyPrice.query().filter(EnergyPrice.year == value.year).one())
        under_threshold = not value.advance_pay
        above_threshold = value.advance_pay
        if value.electric_meter.disconnected:
            under_threshold = False
            above_threshold = False
        content_data = dict(
            deflection='' if member.appellation == 'Frau' else 'r',
            appellation=member.appellation,
            title=member.title,
            lastname=member.direct_debit_account_holder or member.lastname,
            value=format_kwh(value.value),
            usage=format_kwh(value.usage),
            value_last_year=format_kwh(value.value-value.usage),
            meter=value.electric_meter.number,
            whole_price=format_eur(value.whole_price),
            to_pay=format_eur(value.to_pay),
            last_year=value.year-1,
            year=value.year,
            next_year=value.year+1,
            iban=format_iban(member.iban),
            bic=member.bic,
            threshold=format_eur(THRESHOLD),
            advance_pay=format_eur(value.advance_pay_last_year),
            advance_pay_next_year=format_eur(value._advance_pay),
            price_kwh=format_eur(price.price, full=True),
            normal_fee=format_eur(price.normal_fee),
            power_fee=format_eur(price.power_fee),
            no_abschlag=value.to_pay == value.whole_price,
            must_pay=value.to_pay > 0,
            gets_back=value.to_pay <= 0,
            disconnected=value.electric_meter.disconnected,
            under_threshold=under_threshold,
            above_threshold=above_threshold)
        subject = u'Energieabrechnung für Zähler Nr. %s' % (
            value.electric_meter.number)
        yield subject, content_data
