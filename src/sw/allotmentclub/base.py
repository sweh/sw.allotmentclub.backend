# coding:utf8
from __future__ import unicode_literals
from babel.numbers import format_currency


def format_kwh(value):
    return '{} kWh'.format(value if value is not None else '--')


def format_eur(value, full=False):
    if value is None:
        return '---.-- €'
    value = value / 10000.0
    format = '#,##0.00 ¤'
    if full:
        format = '#,##0.0000 ¤'
    return format_currency(
        value, 'EUR', format, currency_digits=False, locale='de_DE')
