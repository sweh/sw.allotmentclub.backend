# encoding=utf8
from __future__ import unicode_literals
from datetime import datetime
from sw.allotmentclub import User, Member, Organization
from sw.allotmentclub.model import ENGINE_NAME
import csv
import json
import os.path
import pkg_resources
import pytest
import risclog.sqlalchemy.testing
import transaction


class JSONFixture(object):

    basepath = ('sw.allotmentclub',
                '../../../../spec/javascripts/fixtures/json/')
    _url = None

    def __init__(self, fixture, key):
        package, path = self.basepath
        self.fixture_path = pkg_resources.resource_filename(
            package, os.path.join(path, fixture))
        self.key = key
        self.fixture = self.load().get(self.key, {})

    def url(self, default=None):
        self._url = self.fixture.get('url', default)
        return self._url

    def load(self):
        with open(self.fixture_path, 'r') as fixture:
            return json.load(fixture)

    def write(self, content):
        with open(self.fixture_path, 'w') as fixture:
            json.dump(content, fixture, sort_keys=True, indent=4,
                      separators=(',', ': '))

    def assertEqual(self, data, data_key, save=False):
        if save:
            fixture = self.load()
            if self.key not in fixture:
                fixture[self.key] = {}
            fixture[self.key]['url'] = self._url
            fixture[self.key][data_key] = data.get(data_key, None)
            self.write(fixture)
            self.fixture = self.load()[self.key]
        expected = self.fixture[data_key] or []
        got = data.get(data_key, [])
        assert len(expected) == len(got)
        for item in expected:
            assert item in got

    def ajax(self, browser):
        """Simulate ajax call with data from fixture."""
        data = self.fixture['data']
        url = data['url'].replace('/api/', '')
        if data.get('type', data.get('method', '')).lower() == 'post':
            browser.post(
                'http://localhost{}'.format(url),
                data=data['data'],
                type=data['contentType'],
                xhr=True)
        else:
            browser.get('http://localhost{}'.format(url), xhr=True)


def assertFileEqual(generated_data, master_filename):
    from pdf_diff.command_line import compute_changes
    import pkg_resources
    import tempfile
    import os
    import pytest
    master_file = pkg_resources.resource_filename(
        'sw.allotmentclub.browser.tests', master_filename)
    handle, generated_file = tempfile.mkstemp(suffix='pdf')
    os.fdopen(handle, 'wb').write(generated_data)
    changes = compute_changes(master_file, generated_file)
    if changes:
        changes_text = ""
        for change in changes:
            if change == '*':
                changes_text += '\n\r'
                continue
            changes_text += '{}: {}\n\r'.format(
                change['pdf']['file'], change['text'])
        pytest.fail(
            'Generated pdf does not equal master: \n\r\n\r{}'.format(
                changes_text))
    else:
        os.remove(generated_file)


def pytest_configure(config):
    import sys
    sys._called_from_test = True


def pytest_unconfigure(config):
    import sys  # This was missing from the manual
    del sys._called_from_test


@pytest.fixture(scope='function')
def json_fixture(request):
    """Helper that retrieves JSON fixtures from files on disk."""
    return JSONFixture(
        request.module.__name__.split('.')[-1].replace('test_', '') + '.json',
        request.function.__name__.replace('test_', ''))


@pytest.fixture(scope='session')
def database_session(request):
    """Set up and tear down the sw.allotmentclub database.

    Returns the database utility object.
    """
    # create pytest fixture for database
    return risclog.sqlalchemy.testing.database_fixture_factory(
        request, 'sw.allotmentclub', ENGINE_NAME, create_all=True)


@pytest.fixture(scope='function')
def database(request, database_session):
    """Perform database setup and tear down for test function.

    Will empty all tables beforehand and close the session afterwards.

    Since this fixture is effectively used in every unit test, we also run the
    cleanup here.

    Returns the database utility object.
    """
    risclog.sqlalchemy.testing.database_test_livecycle_fixture_factory(request)
    return database_session


@pytest.fixture(scope='function')
def organization(request, database):
    """Fixture that creates an organization."""
    org = Organization.find_or_create(id=1, title='Leuna-Siedlung Roter See')
    database.session.flush()
    transaction.commit()
    return org


@pytest.fixture(scope='function')
def verwalter(request, organization, database):
    """Fixture creating a user with role Administrator."""
    user = User.find_or_create(
        username='admin', password='admin',
        vorname='Admin', nachname='istrator',
        unrestricted_access=True,
        organization_id=1)
    database.session.flush()
    transaction.commit()
    return user


@pytest.fixture(scope='function')
def user(request, organization, database):
    """Fixture creating a user with no role."""
    user = User.find_or_create(
        username='user', password='pass', nachname='Mittag',
        position='Vorsitzender', ort='Leuna', organization_id=1)
    database.session.flush()
    return user


@pytest.fixture(scope='function')
def member(request, database):
    """Fixture creating a member."""
    def delete_member():
        Member.query().filter(Member.lastname == 'Mittag').one().delete()
        database.session.flush()

    member = Member.create(firstname='Gerd', lastname='Mittag')
    database.session.flush()
    request.addfinalizer(delete_member)
    return member


class Amount(object):
    amount = None
    currency = None

    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency


def import_bookings():
    from .account import import_transactions, BankingAccount
    account = BankingAccount.find_or_create(
        organization_id=1, number='3440000167')
    statements = []
    with open(pkg_resources.resource_filename(
            'sw.allotmentclub.tests', 'test_account_import.csv')) as f:
        reader = csv.reader(f, delimiter=';')
        for line in reader:
            (_, _, _, account_number, _, _, _, _, _, _, _, bic, _, iban, _, _,
             recipient, _, _, _, _, _, booking_date, _, value, currency, _, _,
             _, _, _, _, _, _, booking_text, _, _, purpose, _, _, _, _, _, _,
             _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
             _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
             _) = line
            statements.append({
                'date': datetime.strptime(booking_date, '%Y/%m/%d'),
                'currency': currency,
                'purpose': purpose,
                'amount': Amount(
                    float(value.replace('/1', ''))/10000,
                    currency),
                'applicant_name': recipient,
                'posting_text': booking_text,
                'applicant_iban': iban,
                'applicant_bin': bic,
                'customer_reference': None
            })
    import_transactions(statements, account)


def import_energy_meters():
    from sw.allotmentclub import Allotment, ElectricMeter, EnergyValue
    from sw.allotmentclub import EnergyPrice
    EnergyPrice.find_or_create(year=2014, value=1342354, bill=42312300,
                               price=3020, normal_fee=81700, power_fee=243300)
    EnergyPrice.find_or_create(year=2015, value=1354334, bill=42134200)
    for allot, number, v2013, v2014, power, disc, comment in [
            ['102', '318992603', '6893', '6893', '', '', ''],
            ['104', '136426011', '10019', '10634', 'X', '', ''],
            ['106', '21785640', '23154', '24207', '', '', ''],
            ['108', '81112116', '8165', '8411', '', '', ''],
            ['110', '31850195', '65811', '66345', '', '', ''],
            ['112', '20232757', '56221', '56371', '', '', ''],
            ['114', '364754', '7361', '7407', 'X', '', ''],
            ['118', '21292097', '935', '960', '', '', ''],
            ['122', '0063487695', '7028', '7988', 'X', '', ''],
            ['124', '4270447', '7671', '8033', '', '', ''],
            ['203', '21181284', '5933', '5997', '', '', ''],
            ['203', '3295328', '1307', '1349', '', '', 'Satanlage'],
            ['249', '20868068', '12115', '12115', '', '', ''],
            ['251', '20236014', '17339', '17352', '', '', 'Wasserpumpe'],
            ['328', '409120', '5075', '5075', '', '', ''],
            ['405', '8056675', '66018', '66098', '', '', '']]:
        allotment = Allotment.query().filter(
            Allotment.number == allot).one()
        meter = ElectricMeter.create(
            allotment=allotment,
            number=number,
            electric_power=bool(power),
            disconnected=bool(disc),
            comment=comment)
        for year, value in [(2013, v2013), (2014, v2014)]:
            value = EnergyValue.create(
                electric_meter=meter, year=year, value=int(value))
            value.update_member()
            value.update_usage()
            value.update_data()
            meter.energy_values.append(value)
        transaction.savepoint()


def import_members(max=99999):
    from sw.allotmentclub import Member, Allotment, Parcel
    for line in [
        ['60', '102', '', 'Frau', 'Ines', 'Groß', 'Mittelweg 7',
            '01458', 'Ottendorf-Okrilla', '', '', ''],
        ['62', '104', '', 'Herr', 'Reiner', 'Pfeil', 'Schillerstr. 42',
         '06247', 'Bad Lauchstädt', '', '034635 32731', ''],
        ['64', '106', '', 'Frau', 'Astrid', 'Ritter',
         'Brandenburgische Str.  27', '15366', 'Hönow', '', '', ''],
        ['67', '108', '', 'Herr', 'Sebastian', 'Wehrmann',
         'Geseniusstr. 34', '06110', 'Halle', '', '', '0172 1096832'],
        ['70', '110', '', 'Herr', 'Johannes', 'Hennig', 'A.-Einstein-'
         'Str. 15', '06237', 'Leuna', '', '03461 502682', ''],
        ['74', '112', '', 'Frau', 'Regina', 'Esser', 'Ringstr. 42',
         '06886', 'Wittenberg', '', '03491 662813', ''],
        ['76', '114', 'Dr.', 'Frau', 'Brigitte', 'Helbig', 'Wolfgang-'
         'Heinze-Str. 20', '04277', 'Leipzig', '', '0341 3520609', ''],
        ['83', '118', '', 'Frau', 'Margit ', 'Götze', 'Heinrich-Heine'
         '-Str. 19', '06237', 'Leuna', '', '03461 811244', ''],
        ['92/93', '122/ 225', '', 'Herr', 'Claus', 'Masthoff', 'Paul-'
         'Thiersch-Str. 16', '06124', 'Halle', '', '0345 6876407', ''],
        ['94/50', '124', '', 'Frau', 'Britta', 'Grimmling', 'Fors 190',
         '87391', 'Bollstabruk', 'Schweden', '', '0157 84943178'],
        ['150', '249/251', '', 'Herr', 'Lutz', 'Rösler',
         'Cloppenburger Str. 12', '06126', 'Halle', '', '', ''],
        ['100/137', '405/406', '', 'Frau', 'Marlies', 'Leutloff', 'Wei'
         'ßenfelser Str. 11c', '06231', 'Bad Dürrenberg', '', '', ''],
        ['', '', '', 'Herr', 'Günter', 'Tillack', 'Harry-S.-Truman-'
         'Allee 4', '14167', 'Berlin', '', '', '0162 9541236'],
        ['153', '328', '', '', '', 'Leuna Bungalowgemeinschaft Roter '
         'See e.V.', 'Postfach 4023', '06233', 'Leuna', '', '', ''],
        ['58', '203', '', '', '', 'Werkstatt', '', '', '', '', '', '']
    ]:
        if '/' in line[0] or '/' in line[1]:
            lines = [line[:], line[:]]
        else:
            lines = [line]

        if '/' in line[0]:
            p1, p2 = line[0].split('/')
            lines[0][0] = p1.strip()
            lines[1][0] = p2.strip()
        if '/' in line[1]:
            p1, p2 = line[1].split('/')
            lines[0][1] = p1.strip()
            lines[1][1] = p2.strip()

        for line in lines:
            member = Member.find_or_create(
                firstname=line[4], lastname=line[5])
            member.title = line[2]
            member.appellation = line[3]
            member.street = line[6]
            member.zip = line[7]
            member.city = line[8]
            member.country = line[9] or 'Deutschland'
            member.phone = line[10]
            member.mobile = line[11]

            if line[1].strip():
                allotment = Allotment.find_or_create(
                    number=int(line[1]), member=member)
                if line[0].strip():
                    Parcel.find_or_create(number=int(line[0]),
                                          allotment=allotment)
            transaction.savepoint()
