"""Add boolean flag for white page to mail attachments.

Revision ID: 1755a035e42a
Revises: 2fd485c59f80
Create Date: 2016-02-01 09:12:26.096538

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1755a035e42a"
down_revision = "2fd485c59f80"


def upgrade():
    op.add_column(
        "attachment",
        sa.Column(
            "white_page_before",
            sa.Boolean(),
            nullable=False,
            server_default="False",
        ),
    )


def downgrade():
    op.drop_column("attachment", "white_page_before")
