# encoding=utf8
from __future__ import unicode_literals
from ..conftest import import_members, import_energy_meters, import_bookings
import datetime


def setUp():
    import_members()
    import_energy_meters()
    import_bookings()


def test_meter_has_values_for_each_year(database):
    from ..electricity import ElectricMeter
    setUp()
    meter = ElectricMeter.get(1)
    assert '318992603' == meter.number
    assert 102 == meter.allotment.number
    assert 'Groß' == meter.allotment.member.lastname
    assert 2 == len(meter.energy_values)  # 2013, 2014
    assert 2013 == meter.energy_values[0].year
    assert 6893 == meter.energy_values[0].value


def test_meter_can_be_replaced_by_another_meter(database):
    from ..electricity import ElectricMeter
    import transaction
    setUp()
    old = ElectricMeter.get(3)
    new = old.replace(100, '0815', 0)
    transaction.commit()
    assert old.allotment == new.allotment
    assert new == old.replaced_by
    assert new.get_last_value(new).member == old.get_last_value(old).member
    assert 0 == new.get_last_value(new).usage
    assert 1053 == old.get_last_value(old).usage


def test_value_has_a_member(database):
    from sw.allotmentclub import EnergyValue, Member
    setUp()
    value = EnergyValue.get(1)
    assert Member.get(1) == value.member


def test_value_can_calculate_usage(database):
    from ..electricity import ElectricMeter
    from ..browser.base import format_kwh
    setUp()
    value = ElectricMeter.query().filter(
        ElectricMeter.number == '81112116').one().energy_values[1]
    value.update_data()
    assert 2014 == value.year
    assert '246 kWh' == format_kwh(value.usage)


def test_value_can_calculate_price(database):
    from ..electricity import ElectricMeter
    from ..browser.base import format_eur
    setUp()
    value = ElectricMeter.query().filter(
        ElectricMeter.number == '81112116').one().energy_values[1]
    value.update_data()
    assert 2014 == value.year
    assert '74,29 €' == format_eur(value.price)
    assert '8,17 €' == format_eur(value.fee)
    assert '82,46 €' == format_eur(value.whole_price)


def add_new_meter_values_to_csv(csv):
    lines = csv.splitlines()
    for index, new_value in enumerate(
            [None, b'6893', b'10812', b'24213', b'8412', b'66345', b'5637',
             b'8000', b'972', b'7988', b'8036']):
        # lines[index] = lines[index].decode('utf-8')
        if new_value is not None:
            lines[index] = lines[index] + new_value
    return b'\n'.join(line for line in lines)


def test__EnergyValue__update_data_1(database):
    """Leaves EnergyValue as is if already discounted."""
    from sw.allotmentclub import EnergyValue
    value = EnergyValue.create(
        value=42, usage=1, price=1, fee=1, whole_price=1, to_pay=1,
        advance_pay=1, discounted=True)
    value.update_data()
    assert value.value == 42
    assert value.price == 1
    assert value.usage == 1
    assert value.fee == 1
    assert value.whole_price == 1
    assert value.to_pay == 1
    assert value.advance_pay == 1


def test__EnergyValue__update_data_2(database):
    """Updates bill data of EnergyValue."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    setUp()
    EnergyPrice.create(
        year=2016, price=3020, normal_fee=81700, power_fee=243300)
    meter = ElectricMeter.get(1)
    value = EnergyValue.create(electric_meter=meter, year=2016, value=7132)
    assert value.price is None
    value.update_member()
    value.update_usage()
    value.update_data()
    assert 239 == value.usage
    assert 721780 == value.price
    assert 81700 == value.fee
    assert value.whole_price == 803500
    assert value.whole_price == value.to_pay
    assert 267800 == value.advance_pay


def test__EnergyValue__update_data_3(database):
    """Member is updated with owner of meter."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, Member, Allotment
    mueller = Member.create(lastname='Müller')
    meyer = Member.create(lastname='Meyer')
    mueller_allotment = Allotment.create(number='123', member=mueller)
    meter = ElectricMeter.create(allotment=mueller_allotment)
    value = EnergyValue.create(electric_meter=meter, year=2016)
    assert value.member is None
    value.update_member()
    assert value.member is mueller
    # Its possible that someone pays the bill explicitely for a meter
    meter.discount_to = meyer
    value.member = None
    value.update_member()
    assert value.member is meyer


def test__EnergyValue__update_data_4(database):
    """Advance pay is zero if under THRESHOLD."""
    from sw.allotmentclub import EnergyValue, ElectricMeter
    from sw.allotmentclub.electricity import THRESHOLD
    setUp()
    value = (EnergyValue.query().join(ElectricMeter)
             .filter(EnergyValue.year == 2014)
             .filter(ElectricMeter.number == '21292097').one())
    assert value.price <= THRESHOLD
    assert value.usage == 25
    assert value.price == 75500
    assert value.advance_pay == 0


def test__EnergyValue__update_data_5(database):
    """Creates bookings for advanced pay for the next year."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Booking, BookingKind, BankingAccount
    setUp()
    BookingKind.create(title='Energieabschlag I')
    BookingKind.create(title='Energieabschlag II')
    BankingAccount.create(number='3')
    EnergyPrice.create(
        year=2016, price=3020, normal_fee=81700, power_fee=243300)
    meter = ElectricMeter.get(1)
    value = EnergyValue.create(electric_meter=meter, year=2016, value=7132)
    assert Booking.query().filter(Booking.accounting_year == 2017).all() == []
    value.update_member()
    value.update_usage()
    value.update_data()
    ap1, ap2 = Booking.query().filter(Booking.accounting_year == 2017).all()
    assert ap1.value == ap2.value == -267800
    assert ap1.member == ap2.member == value.member
    assert ap1.booking_day == datetime.date(2017, 3, 31)
    assert ap2.booking_day == datetime.date(2017, 6, 30)
    assert ap1.purpose == 'Energieabschlag I für Zähler 318992603'
    assert ap2.purpose == 'Energieabschlag II für Zähler 318992603'


def test__EnergyValue__update_data_6(database):
    """Creates multiple bookings for multiple meters of the same allotment."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Booking, BookingKind, BankingAccount
    setUp()
    BookingKind.create(title='Energieabrechnung')
    BookingKind.create(title='Energieabschlag I')
    BankingAccount.create(number='3')
    EnergyPrice.create(
        year=2016, price=3020, normal_fee=81700, power_fee=243300)
    meter = ElectricMeter.get(1)
    value = EnergyValue.create(electric_meter=meter, year=2016, value=7132)
    meter2 = ElectricMeter.get(2)
    value2 = EnergyValue.create(electric_meter=meter2, year=2016, value=14123)
    meter.allotment = meter2.allotment

    assert Booking.query().filter(Booking.accounting_year == 2017).all() == []
    value.update_member()
    value.update_usage()
    value.update_data()
    value2.update_member()
    value2.update_usage()
    value2.update_data()

    ap1, ap2 = Booking.query().filter(Booking.accounting_year == 2017).all()
    assert ap1.value != ap2.value
    assert ap1.member == ap2.member == value.member
    assert ap1.booking_day == ap2.booking_day == datetime.date(2017, 3, 31)
    assert ap1.purpose == 'Energieabschlag I für Zähler 318992603'
    assert ap2.purpose == 'Energieabschlag I für Zähler 136426011'

    enab1, enab2 = Booking.query().filter(
        Booking.accounting_year == 2016).all()
    assert enab1.value != enab2.value
    assert enab1.member == enab2.member == value.member
    assert enab1.booking_day == enab2.booking_day == datetime.date(2016, 8, 31)
    assert enab1.purpose == 'Energieabrechnung für Zähler 318992603'
    assert enab2.purpose == 'Energieabrechnung für Zähler 136426011'


def test__EnergyValue__usage_1(database):
    """Usage is 0 if value is None."""
    from sw.allotmentclub import EnergyValue, ElectricMeter
    assert 0 == EnergyValue.create(electric_meter=ElectricMeter.create(),
                                   year=2016)._usage


def test__EnergyValue__price_1(database):
    """Price is 0 if no EnergyPrice is defined for the year."""
    from sw.allotmentclub import EnergyValue
    assert 0 == EnergyValue.create(year=2016)._price


def test__EnergyValue__price_2(database):
    """Price is 0 if EnergyPrice has no price."""
    from sw.allotmentclub import EnergyValue, EnergyPrice, ElectricMeter
    from sw.allotmentclub import Member, Allotment
    EnergyPrice.create(year=2016)
    assert 0 == EnergyValue.create(
        electric_meter=ElectricMeter.create(
            allotment=Allotment.create(number='123', member=Member.create())),
        year=2016)._price


def test__EnergyValue__price_3(database):
    """Price is price * usage."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Member, Allotment
    EnergyPrice.create(year=2016, price=2)
    assert 200 == EnergyValue.create(
        electric_meter=ElectricMeter.create(
            allotment=Allotment.create(number='123', member=Member.create())),
        year=2016, usage=100)._price


def test__EnergyValue__fee_1(database):
    """Fee is 0 if no energy price."""
    from sw.allotmentclub import EnergyValue
    assert 0 == EnergyValue.create(year=2016)._fee


def test__EnergyValue__fee_2(database):
    """Fee is 0 for disconnected meters."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Allotment, Member
    EnergyPrice.create(year=2016)
    assert 0 == EnergyValue.create(
        electric_meter=ElectricMeter.create(
            allotment=Allotment.create(number='123', member=Member.create()),
            disconnected=True),
        year=2016)._fee


def test__EnergyValue__fee_3(database):
    """Fee is 0 no normal_fee."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Allotment, Member
    EnergyPrice.create(year=2016, normal_fee=12345)
    assert 0 == EnergyValue.create(
        electric_meter=ElectricMeter.create(
            allotment=Allotment.create(number='123', member=Member.create())),
        year=2016)._fee


def test__EnergyValue__fee_4(database):
    """Fee is 0 no power_fee."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Allotment, Member
    EnergyPrice.create(year=2016, power_fee=12345)
    assert 0 == EnergyValue.create(
        electric_meter=ElectricMeter.create(
            allotment=Allotment.create(number='123', member=Member.create())),
        year=2016)._fee


def test__EnergyValue__fee_5(database):
    """Fee is normal_fee if not electic_power."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Allotment, Member
    EnergyPrice.create(year=2016, normal_fee=1, power_fee=3)
    assert 1 == EnergyValue.create(
        electric_meter=ElectricMeter.create(
            allotment=Allotment.create(number='123', member=Member.create()),
            electric_power=False),
        year=2016)._fee


def test__EnergyValue__fee_6(database):
    """Fee is power_fee if electic_power."""
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Allotment, Member
    EnergyPrice.create(year=2016, normal_fee=1, power_fee=3)
    assert 3 == EnergyValue.create(
        electric_meter=ElectricMeter.create(
            allotment=Allotment.create(number='123', member=Member.create()),
            electric_power=True),
        year=2016)._fee


def test__EnergyValue__uodate_data__round_issue(database):
    from sw.allotmentclub import EnergyValue, ElectricMeter, EnergyPrice
    from sw.allotmentclub import Allotment, Member
    from sw.allotmentclub import Booking, BookingKind, BankingAccount
    BookingKind.create(title='Energieabrechnung')
    BankingAccount.create(number='3')
    EnergyPrice.create(
        year=2023,
        normal_fee=98339,
        power_fee=295017,
        price=4177
    )
    member = Member.create()
    value = EnergyValue.create(
        electric_meter=ElectricMeter.create(
            allotment=Allotment.create(
                number='123',
                member=member),
            electric_power=False
        ),
        year=2023,
        usage=51,
        member=member
    )
    value.update_data()
    booking = Booking.query().one()
    assert booking.value == -311300
