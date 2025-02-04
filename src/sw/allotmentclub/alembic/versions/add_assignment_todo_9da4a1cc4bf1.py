"""Add assignment todo

Revision ID: 9da4a1cc4bf1
Revises: 48303c2cf2eb
Create Date: 2023-07-30 13:32:35.422103

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9da4a1cc4bf1"
down_revision = "48303c2cf2eb"


def upgrade():
    op.create_table(
        "assignmenttodo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "priority", sa.Integer(), nullable=False, server_default="4"
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("assignmenttodo")
