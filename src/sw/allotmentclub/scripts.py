# encoding=utf-8
from sw.allotmentclub import Member, Organization, User
from sw.allotmentclub.account import import_transactions_from_fints
from sw.allotmentclub.application import Application
import csv
import datetime
import gocept.logging
import os
import lnetatmo
import pyramid.testing
import pyramid.threadlocal
import requests
import transaction
import xml.etree.ElementTree as ET
import zope.component


ORGANIZATION_ID = 1


def import_members():
    parser = gocept.logging.ArgumentParser(
        description="Import members from excel file.")
    parser.add_argument('-c', '--config', default='portal.ini',
                        help='Specify the config file. (default: portal.ini)')
    parser.add_argument(
        '-i', '--input', default='members.xslx',
        help='Specify the input file. (default: members.xslx)')
    options = parser.parse_args()
    app = Application.from_filename(options.config)
    registry = pyramid.registry.Registry(
        bases=(zope.component.getGlobalSiteManager(),))
    config = pyramid.config.Configurator(
        settings=app.settings, registry=registry)
    config.setup_registry(settings=app.settings)
    request = pyramid.testing.DummyRequest(_registry=registry)
    request.client_addr = '127.0.0.1'
    context = pyramid.threadlocal.manager.get().copy()
    context['request'] = request
    context['registry'] = registry
    pyramid.threadlocal.manager.push(context)
    with open(options.input, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        for id, line in enumerate(reader):
            if id == 0:
                continue
            Member.find_or_create(
                title='',
                appellation='Herr',
                organization_id=2,
                lastname=line[0],
                firstname=line[1],
                street=line[2],
                zip=line[3],
                city=line[4],
                country='Deutschland',
                phone=line[5],
                mobile=line[6],
                email=line[7],
                birthday=line[8])
    transaction.commit()


def import_transactions():
    parser = gocept.logging.ArgumentParser(
        description="Import banking transactions.")
    parser.add_argument('-c', '--config', default='portal.ini',
                        help='Specify the config file. (default: portal.ini)')
    options = parser.parse_args()
    app = Application.from_filename(options.config)
    registry = pyramid.registry.Registry(
        bases=(zope.component.getGlobalSiteManager(),))
    config = pyramid.config.Configurator(
        settings=app.settings, registry=registry)
    config.setup_registry(settings=app.settings)
    request = pyramid.testing.DummyRequest(_registry=registry)
    request.client_addr = '127.0.0.1'
    context = pyramid.threadlocal.manager.get().copy()
    context['request'] = request
    context['registry'] = registry
    pyramid.threadlocal.manager.push(context)
    user = User.by_username('system')
    import_transactions_from_fints(user)


VCF_FILES = {
    1: 'sweh',
    2: 'blauerball'
}


def export_members_vcf():
    parser = gocept.logging.ArgumentParser(
        description="Export members in vcf format.")
    parser.add_argument('-c', '--config', default='portal.ini',
                        help='Specify the config file. (default: portal.ini)')
    options = parser.parse_args()
    Application.from_filename(options.config)
    for organization in Organization.query().all():
        output = ""
        for m in (
                Member.query()
                .filter(Member.organization_id == organization.id)):
            output += """BEGIN:VCARD
VERSION:3.0
PRODID:-//Sebastian Wehrmann//sw.allotmentclub//DE
N:{lastname};{firstname};;;
FN:{firstname} {lastname}
ADR;type=HOME;type=pref:;;{street};{city};;{zip};{country}""".format(
                lastname=m.lastname, firstname=m.firstname, street=m.street,
                city=m.city, zip=m.zip, country=m.country)
            if m.email:
                output += """
EMAIL;type=INTERNET;type=HOME;type=pref:{}""".format(m.email)
            if m.mobile:
                output += """
TEL;type=CELL;type=VOICE;type=pref:{}""".format(m.mobile)
            if m.phone:
                output += """
TEL;type=HOME;type=VOICE:{}""".format(m.phone)
            if m.birthday:
                output += """
BDAY:{}""".format(m.birthday.strftime('%Y%m%d'))
            if m.allotments:
                output += """
NOTE:Bungalow: {}""".format('/'.join(str(a.number) for a in m.allotments))
            output += """
ORG:{org}
REV:{rev}""".format(org=organization.title,
                    rev=datetime.datetime.now().isoformat())
            output += """
UID:{uid}
X-RADICALE-NAME:{uid}.vcf
END:VCARD
""".format(uid=m.id)
        path = os.path.join(os.path.expanduser("~"),
                            '.config/radicale/collections',
                            VCF_FILES[organization.id])
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, 'addressbook.vcf'), 'w') as f:
            f.write(output)


def grab_helios_data(settings):
    payload = {
        "v00003": "de",
        "v01306": "v01306",
        "v00001": "v00001",
        "v00402": settings['helios.pass'],
        "but0": "Anmelden",
    }

    session_requests = requests.session()

    result = session_requests.post(
        'http://10.0.1.64/info.htm',
        data=payload,
        headers=dict(referer='http://10.0.1.64')
    )

    headers = {
        "Host": "10.0.1.64",
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0)"
                       " Gecko/20100101 Firefox/65.0"),
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://10.0.1.64/anzeig.htm",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "Content-Type": "text/plain;charset=UTF-8",
        "Content-Length": "20",
        "Connection": "keep-alive"}

    result = session_requests.post(
        'http://10.0.1.64/data/werte8.xml',
        headers=headers,
        data="xml=/data/werte8.xml",
    )

    data = dict()
    key = None
    for id, child in enumerate(ET.fromstring(result.text)):
        if id == 0:
            continue
        if key is None:
            key = child
        else:
            data[key.text] = child.text
            key = None

    return data


def grab_netatmo_data(settings):
    result = dict()

    # 1 : Authenticate
    authorization = lnetatmo.ClientAuth(
        settings['netatmo.client.id'],
        settings['netatmo.client.secret'],
        settings['netatmo.user'],
        settings['netatmo.pass'],
        scope="read_station")

    # 2 : Get devices list
    weatherData = lnetatmo.WeatherStationData(authorization)

    # 3 : Access most fresh data directly
    station = weatherData.stationByName('Am Wachtelberg')
    for module in station['modules']:
        if module['type'] == 'NAModule1':
            result['wachtelberg_temp_out_battery'] = module['battery_percent']
            result['wachtelberg_out_temp'] = (
                module['dashboard_data']['Temperature'])
            result['wachtelberg_out_humi'] = (
                module['dashboard_data']['Humidity'])
            temp_trend = module['dashboard_data']['temp_trend']
            temp_trend = ('right' if temp_trend == 'stable' else temp_trend)
            result['wachtelberg_out_temp_trend'] = temp_trend
        elif module['type'] == 'NAModule3':
            result['wachtelberg_rain_battery'] = module['battery_percent']
            result['wachtelberg_rain'] = module['dashboard_data']['Rain']
            result['wachtelberg_rain_1'] = (
                module['dashboard_data']['sum_rain_1'])
            result['wachtelberg_rain_24'] = (
                module['dashboard_data']['sum_rain_24'])
        elif module['type'] == 'NAModule2':
            result['wachtelberg_wind_battery'] = module['battery_percent']
            result['wachtelberg_wind_strength'] = (
                module['dashboard_data']['WindStrength'])
            result['wachtelberg_wind_angle'] = (
                module['dashboard_data']['WindAngle'])
        elif module['type'] == 'NAModule4':
            result['wachtelberg_temp_in_battery'] = module['battery_percent']
            result['wachtelberg_in_temp'] = (
                module['dashboard_data']['Temperature'])
            result['wachtelberg_in_humi'] = (
                module['dashboard_data']['Humidity'])
            result['wachtelberg_in_co2'] = module['dashboard_data']['CO2']

    station = weatherData.stationByName('Roter See')
    for module in station['modules']:
        if module['type'] == 'NAModule1':
            result['rotersee_temp_out_battery'] = module['battery_percent']
            result['rotersee_out_temp'] = (
                module['dashboard_data']['Temperature'])
            result['rotersee_out_humi'] = module['dashboard_data']['Humidity']
            temp_trend = module['dashboard_data']['temp_trend']
            temp_trend = ('right' if temp_trend == 'stable' else temp_trend)
            result['rotersee_out_temp_trend'] = temp_trend
        elif module['type'] == 'NAModule3':
            result['rotersee_rain_battery'] = module['battery_percent']
            result['rotersee_rain'] = module['dashboard_data']['Rain']
            result['rotersee_rain_1'] = module['dashboard_data']['sum_rain_1']
            result['rotersee_rain_24'] = (
                module['dashboard_data']['sum_rain_24'])
    result['rotersee_in_temp'] = station['dashboard_data']['Temperature']
    result['rotersee_in_humi'] = station['dashboard_data']['Humidity']
    result['rotersee_in_co2'] = station['dashboard_data']['CO2']
    return result


def grab_dashboard_data():
    from sw.allotmentclub import DashboardData
    parser = gocept.logging.ArgumentParser(
        description="Grab helios data.")
    parser.add_argument('-c', '--config', default='portal.ini',
                        help='Specify the config file. (default: portal.ini)')
    options = parser.parse_args()
    app = Application.from_filename(options.config)
    registry = pyramid.registry.Registry(
        bases=(zope.component.getGlobalSiteManager(),))
    config = pyramid.config.Configurator(
        settings=app.settings, registry=registry)
    config.setup_registry(settings=app.settings)
    request = pyramid.testing.DummyRequest(_registry=registry)
    request.client_addr = '127.0.0.1'
    context = pyramid.threadlocal.manager.get().copy()
    context['request'] = request
    context['registry'] = registry
    pyramid.threadlocal.manager.push(context)

    heliosdata = grab_helios_data(app.settings)
    try:
        netatmodata = grab_netatmo_data(app.settings)
    except Exception:
        netatmodata = dict()

    dashboarddata = DashboardData.create(
        organization_id=ORGANIZATION_ID,
        luefterstufe=heliosdata['v00102'],
        luefter_percent=heliosdata['v00103'],
        luefter_aussenluft=float(heliosdata['v00104']),
        luefter_zuluft=float(heliosdata['v00105']),
        luefter_fortluft=float(heliosdata['v00106']),
        luefter_abluft=float(heliosdata['v00107']),
        luefter_abluft_feuchte=heliosdata['v02136'])

    for k, v in netatmodata.items():
        setattr(dashboarddata, k, v)

    transaction.commit()
