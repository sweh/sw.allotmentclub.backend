# encoding=utf8
from __future__ import unicode_literals
from datetime import datetime
from io import BytesIO
import openpyxl
import transaction


def setUp():
    from sw.allotmentclub.conftest import import_energy_meters, import_members
    import_members()
    import_energy_meters()
    transaction.commit()


def test_can_download_and_upload_energy_list(browser):
    from sw.allotmentclub import EnergyValue, ElectricMeter
    year = datetime.now().year
    setUp()
    assert [8165, 8411] == sorted(
        [v.value for v in ElectricMeter.get(4).energy_values]
    )
    browser.login()
    browser.open('http://localhost/electricity/export')
    wb = openpyxl.load_workbook(BytesIO(browser.contents))
    with open('/Users/sweh/Downloads/test.xlsx', 'wb') as f:
        f.write(browser.contents)
    sheet = wb.get_active_sheet()
    for index, row in enumerate(sheet.rows):
        if index in (0, 1):
            continue
        row[-3].value = row[-4].value or 0 + 100
        row[-1].value = True
        if row[0].value == 4:
            row[-1].value = False
    to_import = BytesIO()
    wb.save(to_import)
    to_import.seek(0)
    browser._upload(
        'http://localhost/electricity/import',
        ('import.xlsx',
         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
         to_import))
    assert 16 == (EnergyValue.query()
                  .filter(EnergyValue.year == year).count())
    assert 1 == (EnergyValue.query()
                 .filter(EnergyValue.year == year)
                 .filter(EnergyValue.estimated_value.is_(True)).count())
    assert [100, 8165, 8411] == sorted(
        [v.value for v in ElectricMeter.get(4).energy_values]
    )
