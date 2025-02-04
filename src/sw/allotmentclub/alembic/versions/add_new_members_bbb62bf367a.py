"""Add new members.

Revision ID: bbb62bf367a
Revises: 2d287284c72e
Create Date: 2015-10-05 09:42:39.792984

"""

from __future__ import unicode_literals

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bbb62bf367a"
down_revision = "2d287284c72e"


def upgrade():
    op.add_column(
        "electricmeter",
        sa.Column("discount_to_id", sa.Integer(), nullable=True),
    )

    # Silvia & Lars Müller verkaufen Bungalow 317 an Andrea und Mario Gille
    op.execute("""
        INSERT into member
            (appellation, firstname, lastname, street, zip, city, country,
             email, direct_debit, get_post) VALUES
            ('Frau', 'Andrea', 'Gille', 'Weberweg 8d', '06805',
             'Bad Schmiedeberg', 'Deutschland', 'andrea-gille@t-online.de',
             false, true);""")
    op.execute("""
        UPDATE allotment SET member_id = (
            SELECT id FROM member WHERE lastname = 'Gille') WHERE id = 151;""")

    # Gerd & Irmgard Mank verkaufen Bungalow 250 an Uwe & Silvia Loos
    op.execute("""
        INSERT into member
            (appellation, firstname, lastname, street, zip, city, country,
             direct_debit, get_post) VALUES
            ('Herr', 'Uwe', 'Loos', 'Teucheler Straße 14b', '06886',
             'Wittenberg', 'Deutschland', false, true);""")
    op.execute("""
        UPDATE allotment SET member_id = (
            SELECT id FROM member WHERE lastname = 'Loos') WHERE id = 137;""")

    # Zähler 4246 geht an Bungalow 335 und Abrechnung an Anke Meister
    op.execute("""
        INSERT into member
            (appellation, firstname, lastname, street, zip, city, country,
             direct_debit, get_post, phone, mobile, bic, iban,
             direct_debit_date) VALUES
            ('Frau', 'Anke', 'Meister', 'Bahnhofstr. 13', '06679',
             'Taucha', 'Deutschland', true, true, '034441 92803',
             '0175 1771334', 'GENODEF1NMB', 'DE58800636480220302200',
             '2015-10-05');""")
    op.execute("""UPDATE electricmeter SET
        discount_to_id = (SELECT id FROM member WHERE lastname = 'Meister'),
        allotment_id = 163 WHERE id = 62;""")

    # Petra Tüttmann verkauft Bungalow 255 an Rene Geißler
    op.execute("""
        INSERT into member
            (appellation, firstname, lastname, street, zip, city, country,
             mobile, direct_debit, get_post) VALUES
            ('Herr', 'Rene', 'Geißler', 'Bleddiner Str. 6', '06901',
             'Kember / OT Globig', 'Deutschland', '0152 218976145',
             false, true);""")
    op.execute("""
        UPDATE allotment SET member_id = (
            SELECT id FROM member WHERE lastname = 'Geißler')
        WHERE id = 141;""")


def downgrade():
    op.drop_column("electricmeter", "discount_to_id")
