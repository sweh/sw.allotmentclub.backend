# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ...conftest import assertFileEqual
from datetime import datetime
import mock
import pytest
import transaction

ENERGIEABRECHNUNG_BODY = """
Sehr geehrte{{deflection}} {{appellation}} {{title}} {{lastname}},

hiermit erhalten Sie Ihre Energieabrechnung für die Periode
{{last_year}}/{{year}}.

Entsprechend der festgelegten Abrechnungsmethode ergibt sich für diesen
Zeitraum ein Preis von {{price_kwh}} / kWh. Die Zählergrundgebühren belaufen
sich bei einem Kraftstromzähler auf {{power_fee}} / Zähler und bei einem
Lichtstromzähler auf {{normal_fee}} / Zähler.

Aufgrund Ihres Verbrauches in Höhe von {{usage}} (Zählerstand {{value}}) ergibt
sich für Sie ein Betrag in Höhe von {{whole_price}}.

{{#if no_abschlag}}
Da Sie im laufenden Jahr keine Energieabschläge zahlen mussten, ist der gesamte
Betrag von **{{to_pay}}** zum 15.10.2015 fällig. Sollten Sie am
Lastschriftverfahren teilnehmen, werden wir den Betrag zum genannten Zeitpunkt
von Ihrem Konto abbuchen. Selbsteinzahler bitten wir, den Betrag bis zum
genannten Zeitpunkt auf unten stehende Bankverbindung zu überweisen.
{{/if}}

{{#if must_pay}}
Abzüglich Ihrer bisher geleisteten Energieabschläge in Höhe von {{advance_pay}}
ist noch ein Restbetrag von **{{to_pay}}** zu zahlen, welcher zum
15.10.{{year}} fällig ist. Sollten Sie am Lastschriftverfahren teilnehmen,
werden wir den Betrag zum genannten Zeitpunkt von Ihrem Konto abbuchen.
Selbsteinzahler bitten wir, den Betrag bis zum genannten Zeitpunkt auf unten
stehende Bankverbindung zu überweisen.
{{/if}}

{{#if gets_back}}
Abzüglich Ihrer bisher geleisteten Energieabschläge in Höhe von {{advance_pay}}
bleibt für Sie ein Guthaben in Höhe von **{{to_pay}}**. Dieses wird zum
15.10.{{year}} auf Ihr Konto mit der Nummer {{iban}} ({{bic}}) überwiesen.
{{/if}}

{{#if above_threshold}}
Entsprechend Ihres Verbrauches über {{usage}} ergeben sich für den
Abrechnungszeitraum {{year}}/{{next_year}} zwei Abschläge in Höhe von
**{{advance_pay_next_year}}**. Diese Beträge werden zum
**31. März {{next_year}}** und **30. Juni {{next_year}}** von Ihrem Bankkonto
eingezogen.
{{/if}}

{{#if under_threshold}}
Da Ihr Verbrauch von {{usage}} in diesem Anrechnungszeitraum einen Abschlag
ergibt, der unter der Bemessungsgrenze von {{threshold}} liegt, sind für Sie
keine Zwischenzahlungen für die Abrechnungsperiode {{year}}/{{next_year}}
erforderlich. Ihre Energieabrechnung erfolgt {{next_year}} vollständig mit der
Endabrechnung im September.
{{/if}}

"""

MISSING_ASSIGMENT_BODY = """
Sehr geehrte{{deflection}} {{appellation}} {{title}} {{lastname}},

als Mitglied der Leuna-Bungalowgemeinschaft Roter See sind Sie verpflichtet,
pro Jahr 5h an Arbeitseinsätzen zu leisten. Als Ersatz für nicht geleistete
Arbeitsstunden wird ein Betrag von 10,00 € pro nicht geleisteter Arbeitsstunde
erhoben.

Im Kalenderjahr {{year}} haben Sie {{assignment_hours}} Stunden an
Arbeitseinsätzen im Verein teilgenommen. Es ergibt sich daher ein fälliger
Ersatzbetrag von **{{to_pay}}**.

{{#if direct_debit}}
Da Sie am Lastschriftverfahren teilnehmen, werden wir den fälligen Betrag zum
30.11.{{year}} von Ihrem Konto mit der Kontonummer {{iban}} ({{bic}}) abbuchen.
{{else}}
Da Sie nicht am Lastschriftverfahren teilnehmen, bitten wir Sie, den fälligen
Betrag bis zum 30.11.{{year}} auf unser Vereinskonto zu überweisen. Sollten Sie
den Betrag bereits überwiesen haben, betrachten Sie diese Aufforderung bitte
als gegenstandslos.
{{/if}}

"""


@pytest.fixture(scope='function')
def setUp():
    from sw.allotmentclub import Member, Message, User
    verein = Member.create(lastname="Verein")
    mustermann = Member.create(lastname="Mustermann", firstname="Max")
    user = User.create(username='sw')
    greeting = ('Sehr geehrte{{deflection}} {{appellation}} '
                '{{title}} {{lastname}},\n\n')
    Message.create(id=242, members=[verein], user=user, accounting_year=2015,
                   subject="Info-Brief",
                   body=greeting+"**Info** an alle Mitglieder")
    Message.create(id=243, members=[mustermann], user=user,
                   accounting_year=2015, subject="Willkommen",
                   body=greeting+"Willkommen im Verein.")
    Message.create(id=244, members=[mustermann], user=user,
                   accounting_year=2016, subject="Beitragsabrechnung",
                   body=greeting)
    transaction.commit()


def test__mail__get_recipient_1(database, setUp):
    """It returns lastname and firstname of member of given message id."""
    from ..mail import get_recipient
    assert get_recipient(243) == "Mustermann, Max"


def test__mail__get_recipient_2(database, setUp):
    """It returns "Alle Mitglieder" if member is `Verein`."""
    from ..mail import get_recipient
    assert get_recipient(242) == "Alle Mitglieder"


def test__mail__get_recipient_3(database, setUp):
    """It returns lastname and firstname of external recipient."""
    from sw.allotmentclub import ExternalRecipient, Message, User
    from ..mail import get_recipient
    muster = ExternalRecipient.create(lastname="Muster", firstname="Max")
    Message.create(id=300, externals=[muster], user=User.get(1))
    assert get_recipient(300) == "Muster, Max"


def test__mail__get_recipient_4(database, setUp):
    """It returns Mehrere Empfänger if multiple recipients."""
    from sw.allotmentclub import ExternalRecipient, Message, User
    from ..mail import get_recipient
    muster = ExternalRecipient.create(lastname="Muster", firstname="Max")
    muster2 = ExternalRecipient.create(lastname="Mustermann", firstname="Max")
    Message.create(id=300, externals=[muster, muster2], user=User.get(1))
    assert get_recipient(300) == "Mehrere Empfänger"


def test__mail__print_or_sent_date_1(database, setUp):
    """It returns printed date if message is printed."""
    from ..mail import print_or_sent_date, Message
    now = datetime(2016, 3, 25, 9, 37)
    msg = Message.get(243)
    msg.printed = now
    assert print_or_sent_date(msg.id) == "25.03.2016 09:37"


def test__mail__print_or_sent_date_2(database, setUp):
    """It returns sent date if message is sent."""
    from ..mail import print_or_sent_date, Message
    now = datetime(2016, 3, 25, 9, 37)
    msg = Message.get(243)
    msg.sent = now
    assert print_or_sent_date(msg.id) == "25.03.2016 09:37"


def test__mail__print_or_sent_date_3(database, setUp):
    """It returns sent date if message is sent and printed."""
    from ..mail import print_or_sent_date, Message
    now = datetime(2016, 3, 25, 9, 37)
    msg = Message.get(243)
    msg.sent = now
    msg.printed = datetime(2011, 1, 1, 1, 11)
    assert print_or_sent_date(msg.id) == "25.03.2016 09:37"


def test__mail__print_or_sent_type_1(database, setUp):
    """It returns `E-Mail` if message is sent."""
    from ..mail import print_or_sent_type, Message
    msg = Message.get(243)
    msg.sent = datetime.now()
    assert print_or_sent_type(msg.id) == "E-Mail"


def test__mail__print_or_sent_type_2(database, setUp):
    """It returns `Brief` if message is printed."""
    from ..mail import print_or_sent_type, Message
    msg = Message.get(243)
    msg.printed = datetime.now()
    assert print_or_sent_type(msg.id) == "Brief"


def test__mail__print_or_sent_type_3(database, setUp):
    "It returns `Brief und E-Mail` if message is sent for multiple Members."
    from ..mail import print_or_sent_type, Message
    msg = Message.get(242)
    msg.printed = datetime.now()
    msg.sent = datetime.now()
    assert print_or_sent_type(msg.id) == "Brief und E-Mail"


def test__mail__MailListView_1(browser, json_fixture, setUp):
    """It displays list of messages."""
    url = json_fixture.url()
    browser.login()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json, 'data')


def test__mail__MailPrintView_1(browser, setUp):
    """It only generates pdfs for recipients without email."""
    from sw.allotmentclub import Message, Member
    message = Message.get(243)
    message.members.append(Member.create(
        email='sw@roter-see.de', street='Musterstrasse'))
    transaction.commit()
    browser.login()
    with mock.patch('sw.allotmentclub.browser.mail.datetime') as dt:
        dt.now.return_value = datetime(2016, 3, 25)
        browser.open('http://localhost/mail/243/download')
    assertFileEqual(browser.contents, 'test_mail_print_1.pdf')


def test__mail__MailPreviewView_1(browser, setUp):
    """It generates pdfs for recipients regardless of email."""
    from sw.allotmentclub import Message, Member
    message = Message.get(243)
    message.members.append(Member.create(
        email='sw@roter-see.de', street='Musterstrasse'))
    transaction.commit()
    browser.login()
    with mock.patch('sw.allotmentclub.browser.letter.datetime') as dt:
        dt.now.return_value = datetime(2016, 3, 25)
        browser.open('http://localhost/mail/243/preview')
    assertFileEqual(browser.contents, 'test_mail_preview_1.pdf')


def test__mail__MailPreviewView_2(browser, setUp):
    """It prints multiple pdf pages for a `Verein` message."""
    browser.login()
    with mock.patch('sw.allotmentclub.browser.letter.datetime') as dt:
        dt.now.return_value = datetime(2016, 3, 25)
        browser.open('http://localhost/mail/242/preview')
    assertFileEqual(browser.contents, 'test_mail_preview_2.pdf')


def test__mail__MailPreviewView_3(browser):
    """It does not print address and date if no member assigned to message."""
    from sw.allotmentclub import Message, User
    Message.create(id=244, user=User.create(), accounting_year=2015,
                   subject="Info-Brief", body="**Info** an alle Mitglieder")
    transaction.commit()
    browser.login()
    browser.open('http://localhost/mail/244/preview')
    assertFileEqual(browser.contents, 'test_mail_preview_3.pdf')


def test__mail__MailPreviewView_4(browser, setUp):
    """It renders attachments to the message."""
    from sw.allotmentclub import Attachment
    import pkg_resources
    data = pkg_resources.resource_stream(
        'sw.allotmentclub.browser.tests', 'test_protocol_print.pdf').read()
    Attachment.create(message_id=243, data=data, mimetype='application/pdf')
    transaction.commit()
    browser.login()
    with mock.patch('sw.allotmentclub.browser.letter.datetime') as dt:
        dt.now.return_value = datetime(2016, 3, 25)
        browser.open('http://localhost/mail/243/preview')
    assertFileEqual(browser.contents, 'test_mail_preview_4.pdf')


def test__mail__MailElectricityPreview_1(browser):
    """It can send Energieabrechnungen."""
    from sw.allotmentclub import Message, User, Member
    from sw.allotmentclub.conftest import import_energy_meters, import_members
    import_members()
    import_energy_meters()
    verein = Member.find_or_create(lastname="Verein")
    Message.create(id=245, members=[verein], user=User.create(),
                   accounting_year=2014, subject="Energieabrechnung",
                   body=ENERGIEABRECHNUNG_BODY)
    transaction.commit()
    browser.login()
    with mock.patch('sw.allotmentclub.browser.letter.datetime') as dt:
        dt.now.return_value = datetime(2016, 3, 25)
        browser.open('http://localhost/mail/245/preview')
    assertFileEqual(browser.contents, 'test_mail_energieabrechnung_1.pdf')


def test__mail__MailAssignmentPreview_1(browser):
    """It can send Fehlende Arbeitsstunden."""
    from sw.allotmentclub import Message, User, Member, Assignment
    from sw.allotmentclub import AssignmentAttendee
    from sw.allotmentclub.conftest import import_members
    from sw.allotmentclub.browser.base import get_selected_year
    import_members()
    assignment = Assignment.find_or_create(day=datetime.now())
    AssignmentAttendee.find_or_create(
        assignment=assignment,
        member=Member.query().filter(Member.lastname == 'Wehrmann').one(),
        hours=5)  # No letter
    AssignmentAttendee.find_or_create(
        assignment=assignment,
        member=Member.query().filter(Member.lastname == 'Hennig').one(),
        hours=3)  # Needs to pay less

    verein = Member.find_or_create(lastname="Verein")
    Message.create(id=245, members=[verein], user=User.create(),
                   accounting_year=get_selected_year(),
                   subject="Fehlende Arbeitsstunden",
                   body=MISSING_ASSIGMENT_BODY)
    transaction.commit()
    browser.login()
    with mock.patch('sw.allotmentclub.browser.letter.datetime') as dt:
        dt.now.return_value = datetime(2016, 3, 25)
        browser.open('http://localhost/mail/245/preview')
    assertFileEqual(browser.contents, 'test_mail_fehlarbeitsstunden_1.pdf')
