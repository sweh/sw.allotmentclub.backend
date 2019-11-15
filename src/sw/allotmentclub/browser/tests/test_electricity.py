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
    assert [8165, 8411] == [v.value for v in
                            ElectricMeter.get(4).energy_values]
    browser.login()
    browser.open('http://localhost/electricity/export')
    wb = openpyxl.load_workbook(BytesIO(browser.contents))
    sheet = wb.get_active_sheet()
    for index, row in enumerate(sheet.rows):
        if index in (0, 1):
            continue
        row[-3].value = row[5].value or 0 + 100
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
    assert [8165, 8411, 100] == [v.value for v in
                                 ElectricMeter.get(4).energy_values]


def test_can_download_sepa_wire_transfer(browser):
    from sw.allotmentclub import EnergyValue
    setUp()
    testvalue1 = EnergyValue.query().filter_by(to_pay=2100600).one()
    testvalue1.to_pay = -1325634
    testvalue1.member.iban = 'DE12345678901234567890'
    testvalue1.member.bic = 'NOLADE21HAL'

    testvalue2 = EnergyValue.query().filter_by(to_pay=120960).one()
    testvalue2.to_pay = -59852
    testvalue2.member.iban = 'DE98765432109876543210'
    testvalue2.member.bic = 'NOLADE21HAL'

    testvalue3 = EnergyValue.query().filter_by(to_pay=534700).one()
    testvalue3.to_pay = -123123

    browser.login()
    browser.open(
        'http://localhost/electricity/export_wire_transfer?for_year=2014'
    )
    assert '<CtrlSum>138.55</CtrlSum>' in browser.contents
    assert '<NbOfTxs>2</NbOfTxs>' in browser.contents
    assert '132.56' in browser.contents
    assert '5.99' in browser.contents
    assert '12.31' not in browser.contents
    assert (
        'Energieabrechnung 2014. Rueckzahlung zuviel gezahlter Abschlaege '
        'fuer Zaehler 20236014') in browser.contents
