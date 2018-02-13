# encoding=utf8
from __future__ import unicode_literals
from .base import to_string, format_eur, format_kwh, boolean, get_selected_year
from pyramid.view import view_config
from sw.allotmentclub import ElectricMeter, EnergyValue, Allotment, Member
from sw.allotmentclub import EnergyPrice
import datetime
import sw.allotmentclub.browser.member
import transaction


def get_discount_to(electric_meter_id, request=None):
    meter = ElectricMeter.get(electric_meter_id)
    allotment = meter.allotment
    if meter.discount_to:
        member = meter.discount_to
    else:
        member = meter.allotment.member
    return '{} ({}, {})'.format(allotment.number, member.lastname,
                                member.firstname)


class Query(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Kraftstrom': boolean,
        'Abgeklemmt': boolean,
        'Bungalow': get_discount_to,
    }
    data_class = {
        'Bungalow': 'expand'
    }
    data_hide = {
        'Kraftstrom': 'phone,tablet',
        'Abgeklemmt': 'phone,tablet',
        'Zählernummer': 'phone',
        'Anmerkung': 'phone',
    }

    def select(self):
        return (
            self.db.query(
                ElectricMeter.id.label('#'),
                ElectricMeter.number.label('Zählernummer'),
                ElectricMeter.id.label('Bungalow'),
                ElectricMeter.electric_power.label('Kraftstrom'),
                ElectricMeter.disconnected.label('Abgeklemmt'),
                ElectricMeter.comment.label('Anmerkung'),
            )
            .select_from(ElectricMeter)
            .outerjoin(Allotment)
            .outerjoin(Member))


@view_config(route_name='electricity_list', renderer='json',
             permission='view')
class ElectricityListView(sw.allotmentclub.browser.base.TableView):

    query_class = Query
    default_order_by = 'electricmeter.id'
    available_actions = [
        dict(url='energy_value_list', btn_class='btn-success',
             icon='fa fa-list', title='Energieabrechnungen'),
        dict(url='advance_pay_value_list', btn_class='btn-success',
             icon='fa fa-list', title='Abschläge'),
        dict(url='energy_meter_export', btn_class='btn-success',
             icon='fa fa-cloud-download', title='Exportieren'),
        dict(url='energy_meter_import', btn_class='btn-success',
             icon='fa fa-cloud-upload', title='Importieren')]


def get_to_pay(energy_value_id, request=None):
    value = EnergyValue.get(energy_value_id)
    member = value.member
    allotments = '/'.join(str(a.number) for a in member.allotments)
    if not allotments:
        allotments = 'n/a'
    return '{} ({}, {})'.format(allotments, member.lastname, member.firstname)


class GlobalEnergyValueQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Verbrauch': format_kwh,
        'Kosten': format_eur,
        'Gebühr': format_eur,
        'Gesamt': format_eur,
        'Offen': format_eur,
        'Abschlag': format_eur,
        'Bungalow': get_to_pay,
    }
    css_classes = {
        'Kosten': 'right',
        'Gebühr': 'right',
        'Verbrauch': 'right',
        'Gesamt': 'right',
        'Offen': 'right',
        'Abschlag': 'right',
    }
    data_class = {
        'Bungalow': 'expand'
    }
    data_hide = {
        'Zähler': 'phone',
        'Verbrauch': 'phone,tablet',
        'Kosten': 'phone,tablet',
        'Gebühr': 'phone,tablet',
        'Gesamt': 'phone',
        'Abschlag': 'phone',
    }

    def select(self):
        return (
            self.db.query(
                EnergyValue.id.label('#'),
                EnergyValue.id.label('Bungalow'),
                ElectricMeter.number.label('Zähler'),
                EnergyValue.usage.label('Verbrauch'),
                EnergyValue.price.label('Kosten'),
                EnergyValue.fee.label('Gebühr'),
                EnergyValue.whole_price.label('Gesamt'),
                EnergyValue.to_pay.label('Offen'),
                EnergyValue.advance_pay.label('Abschlag'),
            )
            .select_from(EnergyValue)
            .outerjoin(ElectricMeter)
            .group_by(EnergyValue.id, ElectricMeter.id)
            .filter(EnergyValue.year == get_selected_year()))


@view_config(route_name='global_energy_value_list', renderer='json',
             permission='view')
class GlobalEnergyValueListView(sw.allotmentclub.browser.base.TableView):

    query_class = GlobalEnergyValueQuery
    year_selection = True
    start_year = 2013
    available_actions = [
        dict(url='calculate_energy_values', btn_class='btn-danger',
             icon='fa fa-refresh', title='Neuberechnen'),
    ]


def rboolean(value, *args, **kw):
    return boolean(not value, *args, **kw)


class EnergyValueQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Zählerstand': format_kwh,
        'Abgelesen': rboolean,
        'Verbrauch': format_kwh,
        'Kosten': format_eur,
        'Gebühr': format_eur,
        'Gesamt': format_eur,
        'Offen': format_eur,
        'Abgerechnet': boolean,
    }
    data_class = {
        'Jahr': 'expand'
    }
    css_classes = {
        'Kosten': 'right',
        'Gebühr': 'right',
        'Verbrauch': 'right',
        'Offen': 'right',
    }
    data_hide = {
        'Zählerstand': 'phone,tablet',
        'Abgelesen': 'phone, tablet',
        'Verbrauch': 'phone',
        'Kosten': 'phone,tablet',
        'Gebühr': 'phone',
        'Rechnung an': 'phone,tablet',
        'Abgerechnet': 'phone,tablet',
    }

    def select(self):
        return (
            self.db.query(
                EnergyValue.id.label('#'),
                EnergyValue.year.label('Jahr'),
                EnergyValue.value.label('Zählerstand'),
                EnergyValue.estimated_value.label('Abgelesen'),
                EnergyValue.usage.label('Verbrauch'),
                EnergyValue.price.label('Kosten'),
                EnergyValue.fee.label('Gebühr'),
                EnergyValue.whole_price.label('Gesamt'),
                EnergyValue.to_pay.label('Offen'),
                (to_string(Member.lastname).concat(', ')
                 .concat(to_string(Member.firstname))
                 .label('Rechnung an')),
                EnergyValue.discounted.label('Abgerechnet'),
            )
            .select_from(EnergyValue)
            .outerjoin(Member)
            .filter(EnergyValue.electric_meter == self.context))


@view_config(route_name='energy_value_list', renderer='json',
             permission='view')
class EnergyValueListView(sw.allotmentclub.browser.base.TableView):

    query_class = EnergyValueQuery
    default_order_by = 'year'


@view_config(route_name='calculate_energy_values', renderer='json',
             permission='view')
class CalculateEnergyValues(sw.allotmentclub.browser.base.View):

    def update_price(self):
        org_id = self.request.user.organization_id
        current_year = get_selected_year()
        price = (EnergyPrice.query()
                 .filter(EnergyValue.organization_id == org_id)
                 .filter(EnergyPrice.year == current_year).one())
        price.usage_hauptzaehler = price.value - (
            EnergyPrice.query()
            .filter(EnergyValue.organization_id == org_id)
            .filter(EnergyPrice.year == current_year-1).one().value)
        price.usage_members = sum(
            e.usage for e in (EnergyValue.query()
                              .filter(EnergyValue.year == current_year)
                              .filter(EnergyValue.organization_id == org_id)))
        price.leakage_current = price.usage_hauptzaehler - price.usage_members
        price.price = price.bill / price.usage_hauptzaehler
        phases = sum(3 if e.electric_power else 1
                     for e in (
                         ElectricMeter.query()
                         .filter(ElectricMeter.disconnected.is_(False))
                         .filter(ElectricMeter.organization_id == org_id)))
        price.normal_fee = price.leakage_current * price.price / phases
        price.power_fee = price.normal_fee * 3

    def update(self):
        self.update_price()
        values = (EnergyValue.query()
                  .filter(EnergyValue.discounted.is_(None))
                  .filter(EnergyValue.year == get_selected_year())
                  .all())
        for value in values:
            value.update_data()


class AdvancePayValueQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Zählerstand': format_kwh,
        'Verbrauch': format_kwh,
        'Abschlag': format_eur,
        'Gesamt': format_eur,
    }
    data_class = {
        'Jahr': 'expand'
    }
    css_classes = {
        'Abschlag': 'right',
        'Verbrauch': 'right',
    }
    data_hide = {
        'Zählerstand': 'phone,tablet',
        'Verbrauch': 'phone',
        'Abschlag': 'phone',
        'Rechnung an': 'phone,tablet',
    }

    def select(self):
        return (
            self.db.query(
                EnergyValue.id.label('#'),
                EnergyValue.year.label('Jahr'),
                EnergyValue.value.label('Zählerstand'),
                EnergyValue.usage.label('Verbrauch'),
                EnergyValue.whole_price.label('Gesamt'),
                EnergyValue.advance_pay.label('Abschlag'),
                (to_string(Member.lastname).concat(', ')
                 .concat(to_string(Member.firstname))
                 .label('Rechnung an')),
            )
            .select_from(EnergyValue)
            .outerjoin(Member)
            .filter(EnergyValue.electric_meter == self.context))


@view_config(route_name='advance_pay_value_list', renderer='json',
             permission='view')
class AdvancePayValueListView(sw.allotmentclub.browser.base.TableView):

    query_class = AdvancePayValueQuery
    default_order_by = 'year'


@view_config(route_name='energy_meter_export', renderer='json',
             permission='view')
class EnergyMeterExporterView(sw.allotmentclub.browser.base.XLSXExporterView):

    filename = 'Stromzaehler'
    title = 'Zählerstände'

    def query(self):
        from sqlalchemy.sql.expression import false
        current_year = get_selected_year()
        return (
            self.db.query(
                ElectricMeter.id.label('#'),
                ElectricMeter.id.label('Nachname'),
                ElectricMeter.id.label('Vorname'),
                Allotment.number.label('Bungalow'),
                ElectricMeter.number.label('Zählernummer'),
                ElectricMeter.id.label('Zähler {}'.format(current_year-3)),
                ElectricMeter.id.label('Zähler {}'.format(current_year-2)),
                ElectricMeter.id.label('Zähler {}'.format(current_year-1)),
                ElectricMeter.id.label('Zähler {}'.format(current_year)),
            )
            .select_from(ElectricMeter)
            .join(Allotment)
            .join(Member)
            .order_by(Allotment.number)
            .filter(ElectricMeter.disconnected == false())
            .filter(ElectricMeter.id != 124)
        )

    def _data(self, query):
        data = super(EnergyMeterExporterView, self)._data(query)
        for item in data:
            item = list(item)
            meter = ElectricMeter.get(item[1])
            if meter.discount_to:
                item[1] = meter.discount_to.lastname
                item[2] = meter.comment or meter.discount_to.firstname
            else:
                item[1] = meter.allotment.member.lastname
                item[2] = meter.comment or meter.allotment.member.firstname
            year = get_selected_year()
            value_sec3last_year = meter.get_value(year-3)
            value_sec2last_year = meter.get_value(year-2)
            value_last_year = meter.get_value(year-1)
            value_current_year = meter.get_value(year)
            item[-4] = self._get_value(value_sec3last_year)
            item[-3] = self._get_value(value_sec2last_year)
            item[-2] = self._get_value(value_last_year)
            item[-1] = self._get_value(value_current_year)
            yield item
        item = [0, 'Hauptzähler', 'kWh', 0, 48328153, '', '', '', '']
        for i in range(-1, -5, -1):
            price = (EnergyPrice.query()
                     .filter(EnergyPrice.year == year+i+1).first())
            if price:
                item[i] = price.value
        yield item
        item = [0, 'Endabrechnung', 'microcent', 0, 48328153, '', '', '', '']
        for i in range(-1, -5, -1):
            price = (EnergyPrice.query()
                     .filter(EnergyPrice.year == year+i+1).first())
            if price:
                item[i] = price.bill
        yield item

    def _get_value(self, value_item):
        if not value_item:
            return ''
        if value_item.estimated_value:
            return (value_item.value, {'color': '#8D0009'})
        return value_item.value


@view_config(route_name='energy_meter_import',
             permission='view',
             renderer='json')
class EnergyMeterImporterView(sw.allotmentclub.browser.base.XLSXImporterView):

    def __call__(self):
        year = datetime.datetime.now().year
        # Sonderbehandlung Satellitenanlage
        meter = ElectricMeter.get(124)
        if meter and not meter.get_value(year):
            last = meter.get_last_value(None, 2015)
            energy_value = EnergyValue.create(
                electric_meter=meter, year=year, value=last.value + 552)
            energy_value.update_member()
            energy_value.update_usage()  # verbrauch berechnen
            meter.energy_values.append(energy_value)
        return super(EnergyMeterImporterView, self).__call__()

    def add_data(self, line):
        year = datetime.datetime.now().year
        if line[1].value == 'Hauptzähler':
            EnergyPrice.find_or_create(year=year).value = line[-1].value
            transaction.savepoint()
            return
        if line[1].value == 'Endabrechnung':
            EnergyPrice.find_or_create(year=year).bill = line[-1].value
            transaction.savepoint()
            return
        meter = ElectricMeter.get(line[0].value)
        if not line[-1].value:
            value = int(line[-2].value)
            estimated = True
        else:
            value = int(line[-1].value)
            cs = line[-1].parent.parent._cell_styles
            estimated = (False if list(cs[line[-1].style_id][0:2]) == [0, 0]
                         else True)
        energy_value = EnergyValue.find_or_create(
            electric_meter=meter, year=year)
        energy_value.value = value
        energy_value.estimated_value = estimated
        meter.energy_values.append(energy_value)
        energy_value.update_member()
        energy_value.update_usage()  # verbrauch berechnen
        transaction.savepoint()


class EnergyPriceQuery(sw.allotmentclub.browser.base.Query):

    formatters = {
        'Stand Hauptzähler': format_kwh,
        'Verbrauch Hauptzähler': format_kwh,
        'Verbrauch Mitglieder': format_kwh,
        'Verluststrom': format_kwh,
        'Preis kWh': format_eur,
        'Grundgebühr': format_eur,
        'Grundgebühr Starkstrom': format_eur,
        'Endabrechnung Energieanbieter': format_eur,
    }
    css_classes = {
        'Stand Hauptzähler': 'right',
        'Verbrauch Hauptzähler': 'right',
        'Verbrauch Mitglieder': 'right',
        'Verluststrom': 'right',
        'Preis kWh': 'right',
        'Grundgebühr': 'right',
        'Grundgebühr Starkstrom': 'right',
        'Endabrechnung Energieanbieter': 'right',
    }
    data_class = {
        'Preis kWh': 'expand'
    }
    data_hide = {
        'Grundgebühr': 'phone',
        'Grundgebühr Starkstrom': 'phone,tablet',
        'Stand Hauptzähler': 'phone,tablet',
        'Verbrauch Hauptzähler': 'phone,tablet',
        'Verluststrom': 'phone',
    }

    def select(self):
        return (
            self.db.query(
                EnergyPrice.id.label('#'),
                EnergyPrice.price.label('Preis kWh'),
                EnergyPrice.normal_fee.label('Grundgebühr'),
                EnergyPrice.power_fee.label('Grundgebühr Starkstrom'),
                EnergyPrice.value.label('Stand Hauptzähler'),
                EnergyPrice.usage_hauptzaehler.label('Verbrauch Hauptzähler'),
                EnergyPrice.usage_members.label('Verbrauch Mitglieder'),
                EnergyPrice.leakage_current.label('Verluststrom'),
                EnergyPrice.bill.label('Endabrechnung Energieanbieter'),
            )
            .select_from(EnergyPrice)
            .filter(EnergyPrice.year == get_selected_year()))


@view_config(route_name='energy_price', renderer='json', permission='view')
class EnergyPriceListView(sw.allotmentclub.browser.base.TableView):

    query_class = EnergyPriceQuery
    year_selection = True
    start_year = 2014
