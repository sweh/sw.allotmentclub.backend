# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import transaction


def setUp():
    from sw.allotmentclub import Depot, User
    user = User.create(username='hans')
    Depot.create(date=datetime.datetime(2014, 11, 27, 7, 21, 45),
                 size=15, data=b'GIF89a????!?,D;', mimetype='image/gif',
                 name='test.gif', user=user)
    transaction.commit()


def test_displays_list_of_depots(browser):
    setUp()
    browser.login()
    browser.open('http://localhost/depots')
    expected = [1, 'test.gif', 'GIF', '15.00 B', '27.11.2014 07:21', 'hans']
    assert expected in browser.json_result


def test_depot_can_be_added_via_json_view(browser):
    from sw.allotmentclub import Depot
    browser.login()
    browser._upload('http://localhost/depots/add')
    assert 'success' == browser.json['status']
    assert 'Transparent.gif' == Depot.query().one().name


def test_depot_can_be_edited_via_json_view(browser):
    from sw.allotmentclub import Depot
    setUp()
    browser.login()
    browser._upload('http://localhost/depots/1/edit')
    now = datetime.datetime.now()
    assert 'success' == browser.json['status']
    assert 1 == len(Depot.query().all())
    browser.open('http://localhost/depots')
    assert [1, 'Transparent.gif', 'GIF', '42.00 B',
            now.strftime('%d.%m.%Y %H:%M'), 'admin'] == browser.json_result[0]


def test_depot_can_not_edit_file_if_mimetype_is_different(browser):
    from sw.allotmentclub import Depot
    setUp()
    depot = Depot.get(1)
    depot.mimetype = 'image/png'
    transaction.savepoint()
    browser.login()
    browser._upload('http://localhost/depots/1/edit')
    assert 'error' == browser.json['status']
    assert (
        'Kann nur Dateien vom gleichen Typ bearbeiten. '
        'alt: image/png, neu: image/gif' == browser.json['message'])
