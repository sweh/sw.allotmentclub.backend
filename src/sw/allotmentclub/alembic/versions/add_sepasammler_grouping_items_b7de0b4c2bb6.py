"""Add SEPASammler grouping items

Revision ID: b7de0b4c2bb6
Revises: 7136a99f680d
Create Date: 2016-06-28 08:47:19.610508

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.schema import CreateSequence, Sequence

# revision identifiers, used by Alembic.
revision = "b7de0b4c2bb6"
down_revision = "7136a99f680d"


def upgrade():
    op.execute("""ALTER TABLE sepasammler RENAME TO sepasammlerentry;""")
    op.execute("CREATE TABLE sepasammler AS SELECT * FROM sepasammlerentry;")
    op.execute("""DELETE FROM sepasammler""")
    op.execute("""ALTER SEQUENCE sepasammler_id_seq RENAME TO
               sepasammlerentry_id_seq""")
    op.execute("""ALTER INDEX sepasammler_pkey RENAME TO
               sepasammlerentry_pkey""")
    op.execute(CreateSequence(Sequence("sepasammler_id_seq")))
    op.alter_column(
        "sepasammler",
        "id",
        nullable=False,
        server_default=sa.text("nextval('sepasammler_id_seq'::regclass)"),
    )
    op.create_unique_constraint("sepasammler_pkey", "sepasammler", ["id"])
    op.drop_column("sepasammler", "ignore_in_reporting")
    op.drop_column("sepasammler", "value")
    op.drop_column("sepasammler", "member_id")
    op.execute("""INSERT into sepasammler (pmtinfid, booking_day,
               accounting_year, kind_id) (SELECT distinct pmtinfid,
               booking_day, accounting_year, kind_id FROM sepasammlerentry)""")
    op.create_foreign_key(
        None, "sepasammler", "bookingkind", ["kind_id"], ["id"]
    )
    op.add_column(
        "sepasammlerentry",
        sa.Column("sepa_sammler_id", sa.Integer(), nullable=True),
    )
    op.execute("""UPDATE sepasammlerentry SET sepa_sammler_id = (
        SELECT id FROM sepasammler WHERE pmtinfid = sepasammlerentry.pmtinfid
    )""")
    op.create_foreign_key(
        None, "sepasammlerentry", "sepasammler", ["sepa_sammler_id"], ["id"]
    )
    op.drop_column("sepasammlerentry", "kind_id")
    op.drop_column("sepasammlerentry", "accounting_year")
    op.drop_column("sepasammlerentry", "pmtinfid")
    op.drop_column("sepasammlerentry", "booking_day")


def downgrade():
    raise NotImplementedError("Not possible.")
