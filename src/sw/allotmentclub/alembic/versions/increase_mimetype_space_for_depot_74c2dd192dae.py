"""Increase mimetype space for depot

Revision ID: 74c2dd192dae
Revises: 2a39970710de
Create Date: 2018-05-28 10:10:39.194098

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "74c2dd192dae"
down_revision = "2a39970710de"


def upgrade():
    op.alter_column("depot", "mimetype", type_=sa.VARCHAR(100))


def downgrade():
    op.alter_column("depot", "mimetype", type_=sa.VARCHAR(30))
