"""Model changes to assignment in order to support jsform.

Revision ID: db99756d70b
Revises: 126c6a200c9f
Create Date: 2015-11-20 12:39:19.449012

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op

revision = "db99756d70b"
down_revision = "126c6a200c9f"


def upgrade():
    op.alter_column(
        "assignmentattendee", "hours", existing_type=sa.REAL(), nullable=True
    )
    op.alter_column(
        "assignmentattendee",
        "member_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "assignmentattendee",
        "member_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "assignmentattendee", "hours", existing_type=sa.REAL(), nullable=False
    )
