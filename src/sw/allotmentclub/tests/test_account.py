from __future__ import unicode_literals

import datetime

import pytest

from ..conftest import Amount, import_bookings


def _getOne():
    from sw.allotmentclub import Booking

    return (
        Booking.query()
        .filter(
            Booking.purpose
            == ("Vereinsbeitrag für 2015 Parzelle 214 Czech / Schroeter")
        )
        .one()
    )


def test_import_via_sparkassen_csv(database):
    from sw.allotmentclub import BankingAccount, Booking

    import_bookings()
    assert 1 == len(BankingAccount.query().all())
    assert 30 == len(Booking.query().all())


def test_imported_bookings_do_contain_iban_and_bic(database):
    import_bookings()
    assert "DE79800537624440000377" == _getOne().iban
    assert "NOLADE21HAL" == _getOne().bic


def test_imported_booking_data(database):
    import_bookings()
    booking = _getOne()
    assert "3440000167" == booking.banking_account.number
    assert "2015-01-19" == booking.booking_day.strftime("%Y-%m-%d")
    assert "GUTSCHRIFT" == booking.booking_text
    assert "Horst Schr\xf6ter u. Frau Ingr" == booking.recipient
    assert 600000 == booking.value


def test_booking_can_be_splitted(database):
    from sw.allotmentclub import Booking

    import_bookings()
    booking = _getOne()
    booking.split(259000)
    assert booking.is_splitted is True
    assert booking.splitted_from_id is None

    splitted = (
        Booking.query().filter(Booking.splitted_from_id == booking.id).all()
    )
    assert 2 == len(splitted)
    assert 259000 == splitted[0].value
    assert 341000 == splitted[1].value


def test_split_booking_failure_1(database):
    from sw.allotmentclub import Booking

    booking = Booking.create(value=10)
    assert booking.split(20) == "Neuer Wert ist zu groß."


def test_split_booking_failure_2(database):
    from sw.allotmentclub import Booking

    booking = Booking.create(value=-10)
    assert booking.split(-20) == "Neuer Wert ist zu klein."


def test_split_booking_failure_3(database):
    from sw.allotmentclub import Booking

    booking = Booking.create(value=10)
    assert booking.split(-20) == "Neuer Wert muss positiv sein."


def test_split_booking_failure_4(database):
    from sw.allotmentclub import Booking

    booking = Booking.create(value=-10)
    assert booking.split(20) == "Neuer Wert muss negativ sein."


def test_split_booking_failure_5(database):
    from sw.allotmentclub import Booking

    booking = Booking.create()
    assert booking.split(0) == "Neuer Wert muss größer oder kleiner 0 sein."


def test_imported_bookings_are_auto_assigned(database, member):
    from sw.allotmentclub import Member

    member = Member.query().one()
    member.iban = "DE79800537624440000377"
    member.bic = "NOLADE21HAL"
    import_bookings()
    booking = _getOne()
    assert "Mittag" == booking.member.lastname


def test_import_sepa_raises_value_error_if_no_sammler(database, member):
    from ..account import BankingAccount, Booking, import_transactions

    account = BankingAccount.find_or_create(
        organization_id=1, number="3440000167"
    )
    statements = [
        {
            "date": datetime.datetime.now(),
            "currency": "EUR",
            "purpose": "Energieabrechnung",
            "amount": Amount(2743.12, "EUR"),
            "applicant_name": "Verein",
            "posting_text": "SAMMEL-LS-EINZUG",
            "applicant_iban": "DE123456778899",
            "applicant_bin": "NOLADE21HAL",
            "customer_reference": (
                "DATUM 14.06.2018, 14.28 UHR ANZAHL 9\n"
                "PII7ebef1ebc3ec4a5185583851c8f7dbb2"
            ),
        }
    ]
    assert 0 == Booking.query().count()
    with pytest.raises(
        ValueError,
        match=(
            r"Keine Sammler zu PmtInfId "
            r"'PII7ebef1ebc3ec4a5185583851c8f7dbb2' gefunden."
        ),
    ):
        import_transactions(statements, account)
    assert 0 == Booking.query().count()


def test_import_sepa_raises_value_error_if_empty_sammler(database, member):
    from ..account import (
        BankingAccount,
        Booking,
        SEPASammler,
        import_transactions,
    )

    account = BankingAccount.find_or_create(
        organization_id=1, number="3440000167"
    )
    SEPASammler.create(
        pmtinfid="PII7ebef1ebc3ec4a5185583851c8f7dbb2",
        booking_day=datetime.datetime.now(),
        accounting_year=2018,
    )
    statements = [
        {
            "date": datetime.datetime.now(),
            "currency": "EUR",
            "purpose": "Energieabrechnung",
            "amount": Amount(2743.12, "EUR"),
            "applicant_name": "Verein",
            "posting_text": "SAMMEL-LS-EINZUG",
            "applicant_iban": "DE123456778899",
            "applicant_bin": "NOLADE21HAL",
            "customer_reference": (
                "DATUM 14.06.2018, 14.28 UHR ANZAHL 9\n"
                "PII7ebef1ebc3ec4a5185583851c8f7dbb2"
            ),
        }
    ]
    assert 0 == Booking.query().count()
    with pytest.raises(
        ValueError,
        match=(
            r"Keine Sammler-Einträge zu PmtInfId "
            r"'PII7ebef1ebc3ec4a5185583851c8f7dbb2' gefunden."
        ),
    ):
        import_transactions(statements, account)
    assert 0 == Booking.query().count()


def test_import_sepa_creates_new_booking_entry_for_open_amount(
    database, member
):
    from ..account import (
        BankingAccount,
        Booking,
        SEPASammler,
        SEPASammlerEntry,
        import_transactions,
    )

    account = BankingAccount.find_or_create(
        organization_id=1, number="3440000167"
    )
    sammler = SEPASammler.create(
        pmtinfid="PII7ebef1ebc3ec4a5185583851c8f7dbb2",
        booking_day=datetime.datetime.now(),
        accounting_year=2018,
    )
    SEPASammlerEntry.create(sepasammler=sammler, value=10000000)
    statements = [
        {
            "date": datetime.datetime.now(),
            "currency": "EUR",
            "purpose": "Energieabrechnung",
            "amount": Amount(2743.12, "EUR"),
            "applicant_name": "Verein",
            "posting_text": "SAMMEL-LS-EINZUG",
            "applicant_iban": "DE123456778899",
            "applicant_bin": "NOLADE21HAL",
            "customer_reference": (
                "DATUM 14.06.2018, 14.28 UHR ANZAHL 9\n"
                "PII7ebef1ebc3ec4a5185583851c8f7dbb2"
            ),
        }
    ]
    assert 0 == Booking.query().count()
    import_transactions(statements, account)
    assert 3 == Booking.query().count()

    assert 27431200 == Booking.get(1).value
    assert 10000000 == Booking.get(2).value
    assert 17431200 == Booking.get(3).value

    assert 1 == Booking.get(2).splitted_from_id
    assert 1 == Booking.get(3).splitted_from_id

    assert "SAMMEL-LS-EINZUG Verrechnet" == Booking.get(2).booking_text
