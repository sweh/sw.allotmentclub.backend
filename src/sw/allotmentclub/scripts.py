import csv
import datetime
import hashlib
import os

import gocept.logging
import pyramid.testing
import pyramid.threadlocal
import risclog.sqlalchemy.interfaces
import transaction
import zope.component

from sw.allotmentclub import Member, Organization, User
from sw.allotmentclub.account import import_transactions_from_fints
from sw.allotmentclub.application import Application

ORGANIZATION_ID = 1


def import_members():
    parser = gocept.logging.ArgumentParser(
        description="Import members from excel file."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="portal.ini",
        help="Specify the config file. (default: portal.ini)",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="members.xslx",
        help="Specify the input file. (default: members.xslx)",
    )
    options = parser.parse_args()
    app = Application.from_filename(options.config)
    registry = pyramid.registry.Registry(
        bases=(zope.component.getGlobalSiteManager(),)
    )
    config = pyramid.config.Configurator(
        settings=app.settings, registry=registry
    )
    config.setup_registry(settings=app.settings)
    request = pyramid.testing.DummyRequest(_registry=registry)
    request.client_addr = "127.0.0.1"
    context = pyramid.threadlocal.manager.get().copy()
    context["request"] = request
    context["registry"] = registry
    pyramid.threadlocal.manager.push(context)
    with open(options.input, "r") as file:
        reader = csv.reader(file, delimiter=";")
        for id, line in enumerate(reader):
            if id == 0:
                continue
            Member.find_or_create(
                title="",
                appellation="Herr",
                organization_id=2,
                lastname=line[0],
                firstname=line[1],
                street=line[2],
                zip=line[3],
                city=line[4],
                country="Deutschland",
                phone=line[5],
                mobile=line[6],
                email=line[7],
                birthday=line[8],
            )
    transaction.commit()


def import_transactions():
    parser = gocept.logging.ArgumentParser(
        description="Import banking transactions."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="portal.ini",
        help="Specify the config file. (default: portal.ini)",
    )
    options = parser.parse_args()
    app = Application.from_filename(options.config)
    registry = pyramid.registry.Registry(
        bases=(zope.component.getGlobalSiteManager(),)
    )
    config = pyramid.config.Configurator(
        settings=app.settings, registry=registry
    )
    config.setup_registry(settings=app.settings)
    request = pyramid.testing.DummyRequest(_registry=registry)
    request.client_addr = "127.0.0.1"
    context = pyramid.threadlocal.manager.get().copy()
    context["request"] = request
    context["registry"] = registry
    pyramid.threadlocal.manager.push(context)
    user = User.by_username("system")
    import_transactions_from_fints(user)


VCF_FILES = {1: "sweh", 2: "blauerball"}


def export_members_vcf():
    parser = gocept.logging.ArgumentParser(
        description="Export members in vcf format."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="portal.ini",
        help="Specify the config file. (default: portal.ini)",
    )
    options = parser.parse_args()
    Application.from_filename(options.config)
    for organization in Organization.query().all():
        output = ""
        for m in (
            Member.query()
            .filter(Member.organization_id == organization.id)
            .filter(Member.leaving_year.is_(None))
        ):
            output += """BEGIN:VCARD
VERSION:3.0
PRODID:-//Sebastian Wehrmann//sw.allotmentclub//DE
N:{lastname};{firstname};;;
FN:{firstname} {lastname}
ADR;type=HOME;type=pref:;;{street};{city};;{zip};{country}""".format(
                lastname=m.lastname,
                firstname=m.firstname,
                street=m.street,
                city=m.city,
                zip=m.zip,
                country=m.country,
            )
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
BDAY:{}""".format(m.birthday.strftime("%Y%m%d"))
            if m.allotments:
                output += """
NOTE:Bungalow: {}""".format("/".join(str(a.number) for a in m.allotments))
            elif m.passive_allotment:
                output += """
NOTE:Bungalow: {}""".format(
                    "/".join(str(a.number) for a in m.passive_allotment)
                )
            output += """
ORG:{org}
REV:{rev}""".format(
                org=organization.title, rev=datetime.datetime.now().isoformat()
            )
            output += """
UID:{uid}
X-RADICALE-NAME:{uid}.vcf
END:VCARD
""".format(uid=m.id)
        path = os.path.join(
            os.path.expanduser("~"),
            ".config/radicale/collections",
            VCF_FILES[organization.id],
        )
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, "addressbook.vcf"), "w") as f:
            f.write(output)


def export_events_ics():
    import sw.allotmentclub.browser.calendar

    parser = gocept.logging.ArgumentParser(
        description="Export events in ics format."
    )
    parser.add_argument(
        "-c",
        "--config",
        default="portal.ini",
        help="Specify the config file. (default: portal.ini)",
    )
    parser.add_argument("-t", "--type", help="The type (Mitglied|Vorstand)")
    options = parser.parse_args()
    assert options.type in ("Mitglied", "Vorstand")

    queries = {
        "Mitglied": sw.allotmentclub.browser.calendar.MitgliederQuery,
        "Vorstand": sw.allotmentclub.browser.calendar.VorstandQuery,
    }

    Application.from_filename(options.config)

    name = (
        "Mitgliederliste" if options.type == "Mitglied" else "Vorstandsliste"
    )
    output = f"""\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:VerwaltungLeunaBundalow
X-WR-CALNAME:Leuna-Siedlung {name}
NAME:Leuna-Siedlung Mitgliederliste
CALSCALE:GREGORIAN
BEGIN:VTIMEZONE
TZID:Europe/Berlin
TZURL:http://tzurl.org/zoneinfo-outlook/Europe/Berlin
X-LIC-LOCATION:Europe/Berlin
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE
"""

    db = zope.component.getUtility(risclog.sqlalchemy.interfaces.IDatabase)
    query = queries[options.type](db, User.by_username("system")).select()
    for event in query:
        m = hashlib.md5()
        m.update("-".join(str(i) for i in event).encode())
        uid = m.hexdigest()
        if event[-2]:
            timestamp = event[4].strftime("%Y%m%dT000000Z")
            start = end = event[4].strftime("%Y%m%d")
            if event[5]:
                end = event[5].strftime("%Y%m%d")
        else:
            timestamp = event[4].strftime("%Y%m%dT%H%M%SZ")
            start = end = event[4].strftime("%Y%m%dT%H%M%S")
            if event[5]:
                end = event[5].strftime("%Y%m%dT%H%M%S")
        output += f"""\
BEGIN:VEVENT
DTSTAMP:{timestamp}
UID:{uid}@roter-see.de
DTSTART;TZID=Europe/Berlin:{start}
DTEND;TZID=Europe/Berlin:{end}
SUMMARY:{event[2]}
LOCATION:{event[3]}
END:VEVENT
"""
    output += "END:VCALENDAR"
    print(output)
