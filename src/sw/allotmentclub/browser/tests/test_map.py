from datetime import datetime

import mock
import pkg_resources
import pytest
import transaction

from sw.allotmentclub.conftest import import_members


@pytest.mark.xfail
def test_MapView__call__1(browser, json_fixture):
    """It returns members and parcels."""
    import_members()
    transaction.commit()
    browser.login()
    url = json_fixture.url()
    browser.open("http://localhost{}".format(url))
    json_fixture.assertEqual(browser.json["data"], "data")
    json_fixture.assertEqual(browser.json["data"], "map")
    json_fixture.assertEqual(browser.json["data"], "map_data")


def test_MapDownloadView__call__1(browser, json_fixture):
    """Map can be downloaded."""
    expected = json_fixture.fixture
    browser.login()
    with mock.patch("sw.allotmentclub.browser.map.datetime") as dt:
        dt.now.return_value = datetime(2015, 2, 24, 8)
        browser.post(
            "http://localhost{}".format(expected["url"]),
            data=expected["data"],
            type=expected["type"],
        )
    # assertFileEqual(browser.contents, 'test_map_print.pdf')
    with open(
        pkg_resources.resource_filename(
            "sw.allotmentclub.browser.tests", "test_map_print.svg"
        ),
        "r",
    ) as f:
        assert f.read() == browser.contents
