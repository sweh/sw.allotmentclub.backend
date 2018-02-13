# encoding=utf-8
from __future__ import unicode_literals
from ..conftest import import_bookings


def _getOne():
    from sw.allotmentclub import Booking
    return Booking.query().filter(
        Booking.purpose == (
            "Vereinsbeitrag für 2015 Parzelle 214 Czech / Schroeter")
    ).one()


def test_import_via_sparkassen_csv(database):
    from sw.allotmentclub import Booking, BankingAccount
    import_bookings()
    assert 1 == len(BankingAccount.query().all())
    assert 30 == len(Booking.query().all())


def test_imported_bookings_do_contain_iban_and_bic(database):
    import_bookings()
    assert 'DE79800537624440000377' == _getOne().iban
    assert 'NOLADE21HAL' == _getOne().bic


def test_imported_booking_data(database):
    import_bookings()
    booking = _getOne()
    assert '3440000167' == booking.banking_account.number
    assert '2015-01-19' == booking.booking_day.strftime('%Y-%m-%d')
    assert 'GUTSCHRIFT' == booking.booking_text
    assert u'Horst Schr\xf6ter u. Frau Ingr' == booking.recipient
    assert 600000 == booking.value


def test_booking_can_be_splitted(database):
    from sw.allotmentclub import Booking
    import_bookings()
    booking = _getOne()
    booking.split(259000)
    assert booking.is_splitted is True
    assert booking.splitted_from_id is None

    splitted = Booking.query().filter(
        Booking.splitted_from_id == booking.id).all()
    assert 2 == len(splitted)
    assert 259000 == splitted[0].value
    assert 341000 == splitted[1].value


def test_split_booking_failure_1(database):
    from sw.allotmentclub import Booking
    booking = Booking.create(value=10)
    assert booking.split(20) == 'Neuer Wert ist zu groß.'


def test_split_booking_failure_2(database):
    from sw.allotmentclub import Booking
    booking = Booking.create(value=-10)
    assert booking.split(-20) == 'Neuer Wert ist zu klein.'


def test_split_booking_failure_3(database):
    from sw.allotmentclub import Booking
    booking = Booking.create(value=10)
    assert booking.split(-20) == 'Neuer Wert muss positiv sein.'


def test_split_booking_failure_4(database):
    from sw.allotmentclub import Booking
    booking = Booking.create(value=-10)
    assert booking.split(20) == 'Neuer Wert muss negativ sein.'


def test_split_booking_failure_5(database):
    from sw.allotmentclub import Booking
    booking = Booking.create()
    assert booking.split(0) == 'Neuer Wert muss größer oder kleiner 0 sein.'


def test_imported_bookings_are_auto_assigned(database, member):
    from sw.allotmentclub import Member
    member = Member.query().one()
    member.iban = 'DE79800537624440000377'
    member.bic = 'NOLADE21HAL'
    import_bookings()
    booking = _getOne()
    assert 'Mittag' == booking.member.lastname
