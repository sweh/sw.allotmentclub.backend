from __future__ import unicode_literals

import xlrd

from ...conftest import import_members


def test_MemberAddView_1(browser, json_fixture):
    """It can add new members via JSON."""
    url = json_fixture.url()
    browser.login()
    browser.post("http://localhost{}".format(url), data="")
    assert "success" == browser.json["status"]
    json_fixture.assertEqual(browser.json, "data")


def test_mv_entrance_list_view(browser):
    import_members()
    browser.login()
    browser.open("http://localhost/members/mv_entrance_list")
    workbook = xlrd.open_workbook(file_contents=browser.contents)
    sheet = workbook.sheets()[0]
    assert sheet.cell(0, 0).value.endswith(" - Liste Einlass MV")
    assert "Esser" == sheet.cell(2, 0).value
    assert "Regina" == sheet.cell(2, 1).value
    assert "112" == sheet.cell(2, 2).value
