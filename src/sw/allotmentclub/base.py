import datetime

from babel.numbers import format_currency


def format_kwh(value):
    return "{} kWh".format(value if value is not None else "--")


def format_eur(value, full=False):
    if value is None:
        return "---.-- €"
    value = value / 10000.0
    format = "#,##0.00 ¤"
    if full:
        format = "#,##0.0000 ¤"
    return format_currency(
        value, "EUR", format, currency_digits=False, locale="de_DE"
    )


def parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, datetime.datetime):
        return value
    fmts = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%d.%m.%Y %H:%M",
        "%d.%m.%Y",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    for fmt in fmts:
        try:
            return datetime.datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    raise ValueError(f"Could not parse {value} into da datetime object")
