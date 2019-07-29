# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import transaction
from ...tests.test_account import import_bookings


def setUp():
    import_bookings()
    transaction.commit()


def test_BookingListView_1(browser, json_fixture):
    """It displays list of bookings."""
    url = json_fixture.url()
    setUp()
    browser.login()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json, 'data')


def test_SplitBookingView_1(browser, json_fixture):
    """It displays a form with one input field for the split value."""
    url = json_fixture.url('/booking/1/split')
    setUp()
    browser.login()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json, 'data')


def test_SplitBookingView_2(browser, json_fixture):
    """It splits booking on form submit."""
    from sw.allotmentclub import Booking
    setUp()
    assert len(Booking.query().all()) == 30
    browser.login()
    json_fixture.ajax(browser)
    assert 'success' == browser.json['status']
    assert Booking.get(1).is_splitted is True
    assert len(Booking.query().all()) == 32


def test_SplitBookingView_3(browser, json_fixture):
    """It shows an error message if split failed."""
    from sw.allotmentclub import Booking
    setUp()
    assert len(Booking.query().all()) == 30
    browser.login()
    json_fixture.ajax(browser)
    assert 'error' == browser.json['status']
    expmsg = 'Neuer Wert muss gr\xf6\xdfer oder kleiner 0 sein.'
    assert expmsg == browser.json['msg']
    assert len(Booking.query().all()) == 30
    assert Booking.get(1).is_splitted is False


def setUpSEPASammlerUpdate(kind_shorttitle):
    from sw.allotmentclub import (
        SEPASammler, Booking, BookingKind, BankingAccount, Member)
    kind = BookingKind.find_or_create(title='', shorttitle=kind_shorttitle)
    sammler = SEPASammler.create(
        booking_day='2016-06-30', accounting_year=2016, kind=kind)
    for value in [-2500, -821300]:
        Booking.find_or_create(
            value=value, banking_account=BankingAccount.find_or_create(),
            accounting_year=2016, kind=kind,
            member=Member.create(direct_debit=True))
    setUp()
    return sammler


def test_SEPASammlerUpdateView_1(browser):
    """Testing SEPASammler Energieabschlag 1."""
    from sw.allotmentclub import SEPASammlerEntry
    sammler = setUpSEPASammlerUpdate('ENA1')
    assert len(SEPASammlerEntry.query().all()) == 0
    browser.login()
    browser.open(
        'http://localhost/accounts/sepa_sammler/{}/update'.format(sammler.id))
    assert len(SEPASammlerEntry.query().all()) == 2
    SEPASammlerEntry.query().filter(SEPASammlerEntry.value == 821300).one()


def test_SEPASammlerUpdateView_2(browser):
    """Testing SEPASammler Energieabschlag 2."""
    from sw.allotmentclub import SEPASammlerEntry
    sammler = setUpSEPASammlerUpdate('ENA1')
    assert len(SEPASammlerEntry.query().all()) == 0
    browser.login()
    browser.open(
        'http://localhost/accounts/sepa_sammler/{}/update'.format(sammler.id))
    assert len(SEPASammlerEntry.query().all()) == 2
    SEPASammlerEntry.query().filter(SEPASammlerEntry.value == 821300).one()


def test_SEPASammlerExportView_1(browser):
    """Testing SEPASammler Energieabschlag 1 XML export."""
    from sw.allotmentclub import SEPASammler, SEPASammlerEntry, BookingKind
    from sw.allotmentclub import Member
    import datetime
    import lxml.etree
    kind = BookingKind.find_or_create(
        title='Energieabschlag I', shorttitle='ENA1')
    sammler = SEPASammler.create(
        booking_day='2018-03-31', accounting_year=2018, kind=kind)
    for iban, value in (('DE12500105170648489890', 2540500),
                        ('EE342200221034126658', 8213400)):
        SEPASammlerEntry.find_or_create(
            sepasammler=sammler, value=value,
            member=Member.create(
                lastname='Müller', direct_debit=True, iban=iban,
                bic='NOLADE21HAL',
                direct_debit_date=datetime.date(2017, 1, 1)))
    setUp()
    browser.login()
    browser.open(
        'http://localhost/accounts/sepa_sammler/{}/export'.format(sammler.id))
    doc = lxml.etree.fromstring(browser.contents.encode('utf-8'))
    assert '1075.39' == doc.find('.//CtrlSum', namespaces=doc.nsmap).text
    assert 'Mueller, ' == doc.findall('.//Nm', namespaces=doc.nsmap)[-1].text
    assert 'MUELLER' == doc.find('.//MndtId', namespaces=doc.nsmap).text


def test_BankingAccountListReportView_1(browser):
    from sw.allotmentclub import Booking, BookingKind, Member
    from ...conftest import assertFileEqual
    import transaction
    kind = BookingKind.find_or_create(
        title='Energieabschlag I', shorttitle='ENA1')
    BookingKind.find_or_create(
        title='Energieabschlag II', shorttitle='ENA2')
    member = Member.find_or_create(lastname='Wehrmann', firstname='Sebastian')
    setUp()
    for b in Booking.query():
        b.kind = kind
        b.member = member
    transaction.commit()

    browser.login()
    browser.open('http://localhost/accounts/report.pdf?for_year=2015')
    assertFileEqual(browser.contents, 'test_account_report_1.pdf')
