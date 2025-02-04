from __future__ import unicode_literals

import datetime

import pkg_resources
import transaction


def setUp():
    from sw.allotmentclub import (
        Protocol,
        ProtocolAttachment,
        ProtocolCommitment,
        ProtocolDetail,
    )

    protocol = Protocol.create(
        day=datetime.datetime(2015, 3, 7, 10),
        title="1. Vorstandssitzung",
        location="Leuna Siedling, Vereinsbungalow",
        attendees="GM, AR, ST, SW",
        accounting_year=2015,
    )
    ProtocolDetail.create(
        protocol=protocol,
        duration="10",
        message="""
**TOP I: Berichte**

- GM berichtet über dies.
- ST über jenes.
- dabei fällt SW auf, dass AR garnicht anwesend ist.

Na sowas.""",
        responsible="GM",
    )
    ProtocolDetail.create(
        protocol=protocol,
        duration="20",
        message="""
**TOP II: Finanzen**

Geld ist genug da. (Sagt ST)""",
        responsible="ST",
    )
    ProtocolCommitment.create(
        protocol=protocol,
        who="SW",
        what="Verwaltungs-Software endlich fertig bekommen",
        when="Mitte 2015",
    )
    ProtocolCommitment.create(
        protocol=protocol,
        who="ST",
        what="Mehr Geld ausgeben",
        when="Ende 2015",
    )
    img = get_test_image()
    ProtocolAttachment.create(
        protocol=protocol,
        name="Anlage I",
        mimetype="image/gif",
        size=len(img),
        data=img,
    )
    transaction.commit()


def get_test_image():
    return pkg_resources.resource_stream(
        "sw.allotmentclub.browser.tests", "assyrian.gif"
    ).read()


def test_protocol_can_have_details(database):
    from sw.allotmentclub import Protocol

    setUp()
    protocol = Protocol.query().one()
    assert 2 == len(protocol.details)
    assert 2 == len(protocol.commitments)
    assert 1 == len(protocol.attachments)


def test_displays_list_of_protocols(browser):
    setUp()
    browser.login()
    browser.open("http://localhost/protocols?for_year=2015")
    expected = [
        1,
        "07.03.2015 10:00",
        "1. Vorstandssitzung",
        "GM, AR, ST, SW",
        "Leuna Siedling, Vereinsbungalow",
    ]
    assert expected in browser.json_result


def test_protocol_can_be_added_via_json_view(browser):
    from sw.allotmentclub import Protocol

    setUp()
    browser.login()
    browser.post("http://localhost/protocols/add", data="")
    assert "success" == browser.json["status"]
    assert 2 == len(Protocol.query().all())


def test_displays_list_of_protocol_details(browser):
    setUp()
    browser.login()
    browser.open("http://localhost/protocols/1/details")
    assert [
        2,
        20,
        "<p><strong>TOP II: Finanzen</strong></p>\n<p>Geld ist "
        "genug da. (Sagt ST)</p>",
        "ST",
    ] in browser.json_result


def test_protocols_can_be_printed_as_pdf(browser):
    setUp()
    browser.login()
    browser.open("http://localhost/protocols/1/print")
    assert browser.contents.decode("latin1").startswith("%PDF-")


# class IProtocolCRUDTest(sw.allotmentclub.browser.testing.SeleniumTestCase):
#
#     @mock.patch('sw.allotmentclub.browser.protocol.datetime_now')
#     def test_protocol_crud(self, now):
#         current_year = datetime.datetime.now().year
#         now.return_value = datetime.datetime(current_year, 2, 20)
#         sel = self.selenium
#         sel.waitForTextPresent('Protokolle')
#         sel.click('link=Protokolle')
#         self.assertEmptyTable()
#         # Protokoll anlegen
#         sel.click('link=Neu')
#         sel.waitForElementPresent('css=input[name=day]')
#         self.enter('input[name=title]', 'Protokoll Vorstandssitzung')
#         self.enter('input[name=attendees]', 'GM, AR, ST, SW')
#         self.enter('input[name=location]', 'Roter See, Vereinsbungalow')
#         sel.click('css=#sub_content button[type=submit]')
#         self.markLineInTable()
#
#         # Protokoll bearbeiten
#         sel.click('link=Bearbeiten')
#         sel.waitForElementPresent('css=input[name=day]')
#         sel.assertValue(
#             'css=input[name=title]', 'Protokoll Vorstandssitzung')
#         self.enter('input[name=attendees]', ', HQ')
#         sel.click('css=#sub_content button[type=submit]')
#         sel.waitForTextPresent('GM, AR, ST, SW, HQ')
#         self.markLineInTable()
#
#         # Protokolldetail hinzufügen
#         sel.click('link=Details')
#         self.assertEmptyTable()
#         sel.click('css=#sub_content a[href=protocol_detail_add]')
#         sel.waitForElementPresent('css=input[name=duration]')
#         self.enter('input[name=duration]', '5')
#         self.enter_markdown(
#             'textarea.md-input', '**TOP I**\n\nBegrüßung der Teilnehmer')
#         self.enter('input[name=responsible]', 'GM')
#         sel.click('css=#sub_content button[type=submit]')
#         self.assertNotEmptyTable()
#         sel.assertText('css=tr.odd td p strong', 'TOP I')
#         self.markLineInTable()
#
#         # Protokolldetail bearbeiten
#         sel.click('link=Details')
#         self.markLineInTable(subcontent=True)
#         sel.click('css=#sub_content a[href=protocol_detail_edit]')
#         sel.waitForElementPresent('css=input[name=duration]')
#         self.enter('input[name=duration]', '0')
#         sel.click('css=#sub_content button[type=submit]')
#         sel.waitForTextPresent('50')
#         self.markLineInTable()
#
#         # Anlagen hinzufügen
#         sel.click('link=Anlagen')
#         self.assertEmptyTable()
#         sel.click('css=#sub_content .btn-success')
#         sel.waitForElementPresent('css=.dz-clickable')
#         self.upload_dz(pkg_resources.resource_filename(
#             'sw.allotmentclub.browser.tests', 'example.gif'))
#         self.assertNotEmptyTable()
#         sel.waitForTextPresent('Anlage I')
#         sel.waitForTextPresent('GIF')
#         sel.waitForTextPresent('1.35 KB')
#
#         # Commitments hinzufügen
#         sel.click('link=Absprachen')
#         self.assertEmptyTable()
#         sel.click('css=#sub_content a[href=protocol_commitment_add]')
#         sel.waitForElementPresent('css=input[name=who]')
#         self.enter('input[name=who]', 'SW')
#         self.enter('input[name=what]', 'Nächste Besprechung vorbereiten')
#         self.enter('input[name=when]', 'KW14')
#         sel.click('css=#sub_content button[type=submit]')
#         self.assertNotEmptyTable()
#
#         # Commitments bearbeiten
#         sel.click('link=Absprachen')
#         self.markLineInTable(subcontent=True)
#         sel.click('css=#sub_content a[href=protocol_commitment_edit]')
#         sel.waitForElementPresent('css=input[name=who]')
#         self.enter('input[name=who]', 'W')
#         sel.click('css=#sub_content button[type=submit]')
#         sel.waitForTextPresent('SWW')
#
#         # PDF laden
#         self.assertPDFEqual(
#             'api/protocols/1/print', 'test_protocol_print.pdf')
#
#         # Protokolldetail löschen
#         sel.click('link=Details')
#         self.markLineInTable(subcontent=True)
#         sel.click('css=#sub_content .btn-danger')
#         self.confirm_delete()
#         self.assertEmptyTable()
#
#         # Commitments löschen
#         sel.click('link=Absprachen')
#         self.markLineInTable(subcontent=True)
#         sel.click('css=#sub_content .btn-danger')
#         self.confirm_delete()
#         self.assertEmptyTable()
