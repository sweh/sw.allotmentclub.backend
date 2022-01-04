"""Add budget for 2022

Revision ID: 7e0a65cb279f
Revises: e44a6f304d17
Create Date: 2022-01-04 11:30:27.433502

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '7e0a65cb279f'
down_revision = 'e44a6f304d17'

BOOKING_KINDS = {
    'Mitgliedsbeitrag': 1,
    'Energieabschlag I': 3,
    'Energieabschlag II': 4,
    'Energieabrechnung': 5,
    'Grundsteuer B': 6,
    'Abwasser': 7,
    'Aufnahmegebühr': 13,
    'Grundbesitzabgabe': 14,
    'Versicherungen': 15,
    'Verwaltung': 16,
    'Aufwandsentschädigungen': 17,
    'Instandhaltung': 18,
    'Energieanbieter': 19,
    'Müll': 20,
    'Vereinsfest': 21,
    'Pacht': 22,
    'Körperschaftssteuer': 23,
    'Arbeitsstunden': 2,
    'Mahn- & Zusatzleistungen': 24,
    'sonstige Einnahmen': 25,
    'sonstige Ausgaben': 26,
    'Satellitenanlage': 27,
}

DATA = {
    2022: {
        'Mitgliedsbeitrag': 7800,
        'Aufnahmegebühr': 100,
        'Mahn- & Zusatzleistungen': 30,
        'Arbeitsstunden': 1300,
        'Körperschaftssteuer': 0,
        'sonstige Einnahmen': 0,
        'Pacht': 621,
        'Verwaltung': -1000,
        'Versicherungen': -850,
        'Müll': -1300,
        'Abwasser': -60,
        'Instandhaltung': -2600,
        'Aufwandsentschädigungen': -9900,
        'Grundsteuer B': -50,
        'Grundbesitzabgabe': -21,
        'sonstige Ausgaben': -90,
        'Vereinsfest': -2500,
        'Satellitenanlage': -300,
        'Energieabrechnung': -200,
        'Energieanbieter': 0,
        'Energieabschlag I': 0,
        'Energieabschlag II': 0,
    },
}


def upgrade():
    for year, budgets in DATA.items():
        for kind, amount in DATA[year].items():
            id_ = BOOKING_KINDS[kind]
            amount = amount * 10000
            op.execute(f"""
INSERT into budget (booking_kind_id, accounting_year, value, organization_id)
VALUES ({id_}, {year}, {amount}, 1);
""")


def downgrade():
    for year in DATA:
        op.execute(f"DELETE FROM budget WHERE accounting_year = {year}")
