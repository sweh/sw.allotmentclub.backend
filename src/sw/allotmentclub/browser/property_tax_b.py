from __future__ import unicode_literals

from pyramid.view import view_config

import sw.allotmentclub.browser.base
from sw.allotmentclub import Allotment, GrundsteuerB, Member, Parcel

from .base import format_eur


class Query(sw.allotmentclub.browser.base.Query):
    data_class = {"Nachname": "expand"}

    data_hide = {
        "Vorname": "phone,tablet",
        "Flurstück": "phone,tablet",
        "Gebühr": "phone,tablet",
        "Bungalow": "phone",
    }

    formatters = {
        "Gebühr": format_eur,
    }

    def select(self):
        return (
            self.db.query(
                GrundsteuerB.id.label("#"),
                Allotment.number.label("Bungalow"),
                Parcel.number.label("Flurstück"),
                Member.lastname.label("Nachname"),
                Member.firstname.label("Vorname"),
                GrundsteuerB.value.label("Gebühr"),
            )
            .select_from(Member)
            .outerjoin(Allotment, Allotment.member_id == Member.id)
            .outerjoin(Parcel)
            .join(GrundsteuerB)
        )


@view_config(route_name="property_tax_b", renderer="json", permission="view")
class GrundsteuerBListView(sw.allotmentclub.browser.base.TableView):
    query_class = Query
    default_order_by = "lastname"
