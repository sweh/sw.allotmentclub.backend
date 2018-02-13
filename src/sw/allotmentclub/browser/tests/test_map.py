# encoding=utf8
from __future__ import unicode_literals
from ...conftest import assertFileEqual
from sw.allotmentclub.conftest import import_members
from datetime import datetime
import transaction
import mock
import pytest


@pytest.mark.xfail
def test_MapView__call__1(browser, json_fixture):
    """It returns members and parcels."""
    import_members()
    transaction.commit()
    browser.login()
    url = json_fixture.url()
    browser.open('http://localhost{}'.format(url))
    json_fixture.assertEqual(browser.json['data'], 'data')
    json_fixture.assertEqual(browser.json['data'], 'map')
    json_fixture.assertEqual(browser.json['data'], 'map_data')


def test_MapDownloadView__call__1(browser, json_fixture):
    """Map can be downloaded."""
    expected = json_fixture.fixture
    browser.login()
    with mock.patch('sw.allotmentclub.browser.map.datetime') as dt:
        dt.now.return_value = datetime(2015, 2, 24, 8)
        browser.post(
            'http://localhost{}'.format(expected['url']),
            data=expected['data'],
            type=expected['type'])
    assertFileEqual(browser.contents, 'test_map_print.pdf')
