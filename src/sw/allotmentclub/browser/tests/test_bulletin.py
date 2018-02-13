# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import transaction


def setUp():
    from sw.allotmentclub import Bulletin, User
    user = User.create(username='hans')
    Bulletin.create(
        date=datetime.datetime(2015, 3, 7, 10),
        subject='Ruhezeiten im Verein',
        user=user,
        content="""
### Mittagsruhe

- täglich 13.00 - 15.00 Uhr (ganzjährig)

### Nachtruhe

- Montag bis Freitag:      22.00 - 08.00 Uhr
- Samstag &amp; Sonntag:    24.00 - 08.00 Uhr

### Genereller Baustop

- jährlich vom 15. Juni bis 31. August.""")
    transaction.commit()


def test_BulletinListView_1(browser, json_fixture):
    """It displays list of bulletins."""
    url = json_fixture.url()
    setUp()
    browser.login()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json, 'data')


def test_BulletinAddView_1(browser, json_fixture):
    """It can add new bulletins via JSON."""
    url = json_fixture.url()
    browser.login()
    browser.post('http://localhost{}'.format(url), data='')
    assert 'success' == browser.json['status']
    json_fixture.assertEqual(browser.json, 'data')


def test_BulletinEditView_1(browser, json_fixture):
    """It can update bulletins from JSON."""
    from sw.allotmentclub import Bulletin
    setUp()
    assert 'Vereinsfest findet statt' != Bulletin.query().one().subject
    browser.login()
    json_fixture.ajax(browser)
    assert 'success' == browser.json['status']
    assert 'Vereinsfest findet statt' == Bulletin.query().one().subject


def test_BulletinDeleteView_1(browser, json_fixture):
    from sw.allotmentclub import Bulletin
    setUp()
    assert 1 == len(Bulletin.query().all())
    browser.login()
    json_fixture.ajax(browser)
    assert 'success' == browser.json['status']
    assert 0 == len(Bulletin.query().all())


def test_bulletins_can_be_printed_as_pdf(browser):
    setUp()
    browser.login()
    browser.open('http://localhost/bulletins/1/print')
    assert browser.contents.decode('latin1').startswith('%PDF-')
