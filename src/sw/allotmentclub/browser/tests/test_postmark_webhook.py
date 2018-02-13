# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import pytest
import transaction

MINIMAL_TEST_PDF_CONTENTS = (
    "JVBERi0xLjEKJcKlwrHDqwoKMSAwIG9iagogIDw8IC9UeXBlIC9DYXRhbG9nCiAgICAgL1Bh"
    "Z2VzIDIgMCBSCiAgPj4KZW5kb2JqCgoyIDAgb2JqCiAgPDwgL1R5cGUgL1BhZ2VzCiAgICAg"
    "L0tpZHMgWzMgMCBSXQogICAgIC9Db3VudCAxCiAgICAgL01lZGlhQm94IFswIDAgMzAwIDE0"
    "NF0KICA+PgplbmRvYmoKCjMgMCBvYmoKICA8PCAgL1R5cGUgL1BhZ2UKICAgICAgL1BhcmVu"
    "dCAyIDAgUgogICAgICAvUmVzb3VyY2VzCiAgICAgICA8PCAvRm9udAogICAgICAgICAgIDw8"
    "IC9GMQogICAgICAgICAgICAgICA8PCAvVHlwZSAvRm9udAogICAgICAgICAgICAgICAgICAv"
    "U3VidHlwZSAvVHlwZTEKICAgICAgICAgICAgICAgICAgL0Jhc2VGb250IC9UaW1lcy1Sb21h"
    "bgogICAgICAgICAgICAgICA+PgogICAgICAgICAgID4+CiAgICAgICA+PgogICAgICAvQ29u"
    "dGVudHMgNCAwIFIKICA+PgplbmRvYmoKCjQgMCBvYmoKICA8PCAvTGVuZ3RoIDU1ID4+CnN0"
    "cmVhbQogIEJUCiAgICAvRjEgMTggVGYKICAgIDAgMCBUZAogICAgKEhlbGxvIFdvcmxkKSBU"
    "agogIEVUCmVuZHN0cmVhbQplbmRvYmoKCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1MzUgZiAK"
    "MDAwMDAwMDAxOCAwMDAwMCBuIAowMDAwMDAwMDc3IDAwMDAwIG4gCjAwMDAwMDAxNzggMDAw"
    "MDAgbiAKMDAwMDAwMDQ1NyAwMDAwMCBuIAp0cmFpbGVyCiAgPDwgIC9Sb290IDEgMCBSCiAg"
    "ICAgIC9TaXplIDUKICA+PgpzdGFydHhyZWYKNTY1CiUlRU9GCg==")


@pytest.fixture(scope='function')
def setUp():
    from sw.allotmentclub import Member, Message, User, SentMessageInfo
    mustermann = Member.create(lastname="Mustermann", firstname="Max",
                               email='max@mustermann.de')
    user = User.create(username='sw')
    msg = Message.create(id=242, members=[mustermann], user=user,
                         accounting_year=2016, subject="Test", body="")
    SentMessageInfo.create(message=msg, tag='foo@vorstand.roter-see.de',
                           address='max@mustermann.de')
    transaction.commit()


def test__mail__postmark_webhook_1(browser, setUp):
    """It saves the open status when messages opens."""
    from sw.allotmentclub import SentMessageInfo
    browser.post('http://localhost/mail/postmark_open_tracking_webhook',
                 data={"FirstOpen": True,
                       "Client": {"Name": "Chrome 35.0.1916.153",
                                  "Company": "Google",
                                  "Family": "Chrome"},
                       "OS": {"Name": "OS X 10.7 Lion",
                              "Company": "Apple Computer, Inc.",
                              "Family": "OS X 10"},
                       "Platform": "WebMail",
                       "UserAgent": "Mozilla\/5.0 (Macintosh Safari\/537.36)",
                       "ReadSeconds": 5,
                       "Geo": {"CountryISOCode": "RS",
                               "Country": "Serbia",
                               "RegionISOCode": "VO",
                               "Region": "Autonomna Pokrajina Vojvodina",
                               "City": "Novi Sad",
                               "Zip": "21000",
                               "Coords": "45.2517,19.8369",
                               "IP": "188.2.95.4"},
                       "MessageID": "asdadasd",
                       "ReceivedAt": "2016-11-23T07:03:45",
                       "Tag": "foo@vorstand.roter-see.de",
                       "Recipient": "max@mustermann.de"})
    status = SentMessageInfo.query().one().status
    assert (
        'Geöffnet am 23.11.2016 13:03 Uhr in Novi Sad (IP: 188.2.95.4) '
        'für 5 Sekunden.' == status)


def test__mail__postmark_webhook_2(browser, setUp):
    """It creates new status for addresses not in db."""
    from sw.allotmentclub import SentMessageInfo
    browser.post('http://localhost/mail/postmark_open_tracking_webhook',
                 data={"ReadSeconds": 5,
                       "Geo": {"City": "Novi Sad",
                               "IP": "188.2.95.4"},
                       "Tag": "foo@vorstand.roter-see.de",
                       "ReceivedAt": "2014-06-01T12:00:00",
                       "Recipient": "sebastian.wehrmann@icloud.com"})
    assert 2 == len(SentMessageInfo.query().all())
    status = SentMessageInfo.query().filter(
        SentMessageInfo.address == 'sebastian.wehrmann@icloud.com').one()
    assert status is not None


def test__mail__postmark_webhook_3(browser, setUp):
    """It creates bounce status when message was bounced."""
    from sw.allotmentclub import SentMessageInfo
    browser.post('http://localhost/mail/postmark_open_tracking_webhook',
                 data={"ID": 42,
                       "Type": "HardBounce",
                       "TypeCode": 1,
                       "Name": "Hard bounce",
                       "Tag": "foo@vorstand.roter-see.de",
                       "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
                       "ServerId": 23,
                       "Description": (
                           "The server was unable to deliver your "
                           "message (ex: unknown user, mailbox not found)."),
                       "Details": "Test bounce details",
                       "Email": "max@mustermann.de",
                       "From": "vorstand@roter-see.de",
                       "BouncedAt": "2014-08-01T13:28:10.2735393-04:00",
                       "DumpAvailable": True,
                       "Inactive": True,
                       "CanActivate": True,
                       "Subject": "Test subject"})
    status = SentMessageInfo.query().one().status
    assert ('Hard bounce am 01.08.2014 19:28 Uhr: The server was unable to '
            'deliver your message (ex: unknown user, mailbox not '
            'found).' == status)


def test__mail__postmark_webhook_4(browser, setUp):
    """It creates delivered status when message was delivered."""
    from sw.allotmentclub import SentMessageInfo
    browser.post('http://localhost/mail/postmark_open_tracking_webhook',
                 data={"ServerId": 23,
                       "MessageID": "883953f4-6105-42a2-a16a-77a8eac79483",
                       "Recipient": "max@mustermann.de",
                       "Tag": "foo@vorstand.roter-see.de",
                       "DeliveredAt": "2014-08-01T13:28:10.2735393-04:00",
                       "Details": "Test delivery webhook details"})
    status = SentMessageInfo.query().one().status
    assert 'Zugestellt am 01.08.2014 19:28 Uhr.' == status


def test__mail__postmark_webhook_5(browser, setUp):
    """It updates status for multiple requests."""
    from sw.allotmentclub import SentMessageInfo
    browser.post('http://localhost/mail/postmark_open_tracking_webhook',
                 data={"Recipient": "max@mustermann.de",
                       "Tag": "foo@vorstand.roter-see.de",
                       "DeliveredAt": "2014-08-01T13:28:10.2735393-04:00"})
    browser.post('http://localhost/mail/postmark_open_tracking_webhook',
                 data={"ReadSeconds": 5,
                       "Geo": {"City": "Novi Sad",
                               "IP": "188.2.95.4"},
                       "ReceivedAt": "2016-11-23T07:03:45",
                       "Tag": "foo@vorstand.roter-see.de",
                       "Recipient": "max@mustermann.de"})
    status = SentMessageInfo.query().one().status
    assert (
        'Geöffnet am 23.11.2016 13:03 Uhr in Novi Sad (IP: 188.2.95.4) '
        'für 5 Sekunden.' == status)


def test__mail__postmark_inbound_webhook_1(browser):
    """It creates an inbound email for every request."""
    from sw.allotmentclub import Message, User
    user = User.find_or_create(username='system')
    browser.post(
        'http://localhost/mail/postmark_inbound_webhook',
        data={"FromName": "Postmarkapp Support",
              "From": "support@postmarkapp.com",
              "FromFull": {
                  "Email": "support@postmarkapp.com",
                  "Name": "Postmarkapp Support",
                  "MailboxHash": ""
              },
              "To": ("\"Firstname Lastname\" "
                     "<yourhash+SampleHash@inbound.postmarkapp.com>"),
              "ToFull": [
                  {
                      "Email": "yourhash+SampleHash@inbound.postmarkapp.com",
                      "Name": "Firstname Lastname",
                      "MailboxHash": "SampleHash"
                  }
              ],
              "Cc": ("\"First Cc\" "
                     "<firstcc@postmarkapp.com>, secondCc@postmarkapp.com>"),
              "CcFull": [
                  {
                      "Email": "firstcc@postmarkapp.com",
                      "Name": "First Cc",
                      "MailboxHash": ""
                  },
                  {
                      "Email": "secondCc@postmarkapp.com",
                      "Name": "",
                      "MailboxHash": ""
                  }
              ],
              "OriginalRecipient": "SampleHash@inbound.postmarkapp.com",
              "Subject": "Test subject",
              "MessageID": "73e6d360-66eb-11e1-8e72-a8904824019b",
              "ReplyTo": "replyto@postmarkapp.com",
              "MailboxHash": "SampleHash",
              # "Date": "Fri, 1 Aug 2014 16:45:32 -04:00",
              "Date": "Sat, 19 Aug 2017 19:37:23 +0200 (Mitteleurop?ische",
              "TextBody": "This is a test text body.",
              "HtmlBody": ("<html><body><p>"
                           "This is a test html body."
                           "<\/p><\/body><\/html>"),
              "StrippedTextReply": "This is the reply text",
              "Tag": "TestTag",
              "Headers": [
                  {
                      "Name": "X-Header-Test",
                      "Value": ""
                  },
                  {
                      "Name": "X-Spam-Status",
                      "Value": "No"
                  },
                  {
                      "Name": "X-Spam-Score",
                      "Value": "-0.1"
                  },
                  {
                      "Name": "X-Spam-Tests",
                      "Value": "DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,SPF_PASS"
                  }
              ],
              "Attachments": [
                  {
                      "Name": "test.pdf",
                      "Content": MINIMAL_TEST_PDF_CONTENTS,
                      "ContentType": "application/pdf",
                      "ContentLength": 739
                  }
              ]})
    mail = Message.query().one()
    assert 'support@postmarkapp.com' == mail.externals[0].email
    assert 'Postmarkapp Support' == mail.externals[0].lastname
    assert [] == mail.members
    assert "Test subject" == mail.subject
    assert user == mail.user
    assert mail.inbound is True
    assert ("<html><body><p>"
            "This is a test html body."
            "<\/p><\/body><\/html>" == mail.body)
    assert 1 == len(mail.attachments)
    assert MINIMAL_TEST_PDF_CONTENTS.encode() == base64.b64encode(
        mail.attachments[0].data)
    assert 'application/pdf' == mail.attachments[0].mimetype
    assert 'test.pdf' == mail.attachments[0].filename
    assert int(mail.attachments[0].size) == len(mail.attachments[0].data)
