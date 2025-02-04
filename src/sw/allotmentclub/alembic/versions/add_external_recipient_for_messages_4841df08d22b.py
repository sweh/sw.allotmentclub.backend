"""Add external recipient for messages.

Revision ID: 4841df08d22b
Revises: 45d928fd0cb7
Create Date: 2016-03-30 12:44:52.036678

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4841df08d22b"
down_revision = "45d928fd0cb7"


def upgrade():
    op.create_table(
        "externalrecipient",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=20), nullable=True),
        sa.Column("appellation", sa.String(length=20), nullable=True),
        sa.Column("firstname", sa.String(length=50), nullable=True),
        sa.Column("lastname", sa.String(length=50), nullable=True),
        sa.Column("street", sa.String(length=100), nullable=True),
        sa.Column("zip", sa.String(length=6), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=True),
        sa.Column("country", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "message", sa.Column("external_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "externalrecipient_message",
        "message",
        "externalrecipient",
        ["external_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "externalrecipient_message", "message", type_="foreignkey"
    )
    op.drop_column("message", "external_id")
    op.drop_table("externalrecipient")
