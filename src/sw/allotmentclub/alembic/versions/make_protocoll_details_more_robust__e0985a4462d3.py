"""Make protocoll details more robust against wrong user input.

Revision ID: e0985a4462d3
Revises: 668759e73b80
Create Date: 2017-09-18 06:58:53.031849

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e0985a4462d3"
down_revision = "668759e73b80"


def upgrade():
    op.execute("UPDATE protocoldetail SET duration=0 WHERE duration is null")
    op.alter_column(
        "protocoldetail",
        "duration",
        existing_type=sa.INTEGER(),
        nullable=False,
        server_default="0",
    )
    op.execute("UPDATE protocoldetail SET message='' WHERE message is null")
    op.alter_column(
        "protocoldetail",
        "message",
        existing_type=sa.TEXT(),
        nullable=False,
        server_default="",
    )
    op.execute(
        "UPDATE protocoldetail SET responsible='' WHERE responsible is null"
    )
    op.alter_column(
        "protocoldetail",
        "responsible",
        existing_type=sa.VARCHAR(length=2),
        nullable=False,
        server_default="",
    )


def downgrade():
    op.alter_column(
        "protocoldetail",
        "responsible",
        existing_type=sa.VARCHAR(length=2),
        nullable=True,
    )
    op.alter_column(
        "protocoldetail", "message", existing_type=sa.TEXT(), nullable=True
    )
    op.alter_column(
        "protocoldetail", "duration", existing_type=sa.INTEGER(), nullable=True
    )
