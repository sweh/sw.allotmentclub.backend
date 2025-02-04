"""Add missing foreignkey constraints.

Revision ID: 2fd485c59f80
Revises: db99756d70b
Create Date: 2015-12-18 14:40:07.640937

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2fd485c59f80"
down_revision = "db99756d70b"


def upgrade():
    op.execute("""DELETE FROM booking WHERE member_id = 119;""")
    op.execute("""UPDATE booking SET kind_id = 3 WHERE kind_id = 9;""")
    op.execute("""UPDATE booking SET kind_id = 4 WHERE kind_id = 10;""")
    op.create_foreign_key(
        None, "booking", "booking", ["splitted_from_id"], ["id"]
    )
    op.create_foreign_key(None, "booking", "member", ["member_id"], ["id"])
    op.create_foreign_key(None, "booking", "bookingkind", ["kind_id"], ["id"])
    op.create_foreign_key(
        None, "bookingkind", "bankingaccount", ["banking_account_id"], ["id"]
    )
    op.create_foreign_key(
        None, "electricmeter", "member", ["discount_to_id"], ["id"]
    )
    op.create_foreign_key(None, "energyvalue", "member", ["member_id"], ["id"])
    op.create_foreign_key(None, "formletter", "user", ["user_id"], ["id"])
    op.create_foreign_key(None, "message", "user", ["user_id"], ["id"])


def downgrade():
    op.drop_constraint(None, "message", type_="foreignkey")
    op.drop_constraint(None, "formletter", type_="foreignkey")
    op.drop_constraint(None, "energyvalue", type_="foreignkey")
    op.drop_constraint(None, "electricmeter", type_="foreignkey")
    op.drop_constraint(None, "bookingkind", type_="foreignkey")
    op.drop_constraint(None, "booking", type_="foreignkey")
    op.drop_constraint(None, "booking", type_="foreignkey")
    op.drop_constraint(None, "booking", type_="foreignkey")
