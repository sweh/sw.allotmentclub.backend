"""Remove dashboard

Revision ID: d0bfe38ddce2
Revises: 7e15fdd9747a
Create Date: 2021-02-10 13:32:51.989465

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d0bfe38ddce2"
down_revision = "7e15fdd9747a"


def upgrade():
    op.drop_table("dashboarddata")


def downgrade():
    op.create_table(
        "dashboarddata",
        sa.Column(
            "organization_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "date",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "luefterstufe", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "luefter_percent",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "luefter_abluft_feuchte",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "luefter_aussenluft",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "luefter_zuluft",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "luefter_fortluft",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "luefter_abluft",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "rotersee_temp_out_battery",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "rotersee_rain_battery",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "rotersee_out_temp",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "rotersee_in_temp",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "rotersee_out_humi",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "rotersee_in_humi",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "rotersee_in_co2", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "rotersee_rain", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "rotersee_rain_1", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "rotersee_rain_24",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "rotersee_out_temp_trend",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_temp_out_battery",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_temp_in_battery",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_rain_battery",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_wind_battery",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_out_temp",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_in_temp",
            sa.NUMERIC(precision=3, scale=1),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_out_humi",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_in_humi",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_in_co2",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_rain",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_rain_1",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_rain_24",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_wind_strength",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_wind_angle",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "wachtelberg_out_temp_trend",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("date", name="dashboarddata_pkey"),
    )
