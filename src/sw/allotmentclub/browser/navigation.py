from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

from sw.allotmentclub.browser.base import View, route_permitted, route_url

NAVIGATION_ITEMS = (
    # Title and route
    ("Startseite", "home", "fa-home", None),
    ("Ablage", "depots", "fa-inbox", None),
    ("Aushänge", "bulletins", "fa-thumb-tack", None),
    ("Kalender <sup>beta</sup>", "calendar", "fa-calendar", None),
    ("Protokolle", "protocols", "fa-book", None),
    ("Schlüsselbuch", "keylists", "fa-key", None),
    (
        "Arbeitseinsätze",
        "assignments",
        "fa-wrench",
        (
            ("Übersicht", "assignments"),
            ("Tätigkeiten", "assignment_todos"),
            ("Abrechnung", "member_assignments"),
        ),
    ),
    (
        "Mitglieder",
        "member_list",
        "fa-user",
        (
            ("Aktive", "member_list"),
            ("Passive", "member_list_passive"),
            ("Pächter", "member_list_leased"),
            ("Trinkwasser", "member_list_tap_water"),
        ),
    ),
    (
        "Lageplan",
        "map",
        "fa-location-arrow",
        (
            ("Übersicht", "map"),
            ("Flurstücke", "parcel_list"),
        ),
    ),
    (
        "Postversand",
        "mail_list_inbox",
        "fa-envelope-square",
        (
            ("Posteingang", "mail_list_inbox"),
            ("Entwürfe", "mail_list_drafts"),
            ("Gesendet", "mail_list_sent"),
            ("Externe Empfänger", "externals"),
        ),
    ),
    (
        "Energie",
        "electricity_list",
        "fa-lightbulb-o",
        (
            ("Stromzähler", "electricity_list"),
            ("Abrechnungen", "global_energy_value_list"),
            ("Kennzahlen", "energy_price"),
        ),
    ),
    ("Abwasser", "waste_water", "fa-recycle", None),
    ("Grundsteuer B", "property_tax_b", "fa-university", None),
    (
        "Finanzen",
        "booking_list",
        "fa-credit-card",
        (
            ("Übersicht", "banking_account_list"),
            ("Vereins-Konto", "booking_list"),
            ("Mitgliedskonten", "member_account_list"),
            ("SEPA-Lastschriften", "sepa_direct_debit"),
            ("SEPA-Sammler", "sepa_sammler_list"),
        ),
    ),
    ("Berechtigungen", "access_authority", "fa-unlock", None),
)


@view_config(
    route_name="navigation", permission=NO_PERMISSION_REQUIRED, renderer="json"
)
class NavigationView(View):
    def __call__(self):
        result = []
        for title, route, css, sublinks in NAVIGATION_ITEMS:
            if not route_permitted(route, self.request):
                continue
            url = route_url(route, self.request)
            entry = {"route": route, "title": title, "url": url, "css": css}
            if sublinks is not None:
                subentries = []
                for title, route in sublinks:
                    if not route_permitted(route, self.request):
                        continue
                    subentries.append(
                        {
                            "route": route,
                            "title": title,
                            "url": route_url(route, self.request),
                        }
                    )
                if subentries:
                    entry["subs"] = subentries
            result.append(entry)
        return {"status": "success", "data": result}
