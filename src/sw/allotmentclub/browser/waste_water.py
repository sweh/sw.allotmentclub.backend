# encoding=utf8
from __future__ import unicode_literals
from .base import format_eur
from pyramid.view import view_config
from sw.allotmentclub import Member, Allotment, Parcel, Abwasser
import sw.allotmentclub.browser.base


class Query(sw.allotmentclub.browser.base.Query):

    data_class = {
        'Nachname': 'expand'
    }

    data_hide = {
        'Vorname': 'phone,tablet',
        'Flurstück': 'phone,tablet',
        'Gebühr': 'phone,tablet',
        'Bungalow': 'phone',
    }

    formatters = {
        'Gebühr': format_eur,
    }

    def select(self):
        return (
            self.db.query(
                Abwasser.id.label('#'),
                Allotment.number.label('Bungalow'),
                Parcel.number.label('Flurstück'),
                Member.lastname.label('Nachname'),
                Member.firstname.label('Vorname'),
                Abwasser.value.label('Gebühr'),
            )
            .select_from(Member)
            .outerjoin(Allotment)
            .outerjoin(Parcel)
            .join(Abwasser)
        )


@view_config(route_name='waste_water', renderer='json', permission='view')
class MemberListView(sw.allotmentclub.browser.base.TableView):

    query_class = Query
    default_order_by = 'lastname'
