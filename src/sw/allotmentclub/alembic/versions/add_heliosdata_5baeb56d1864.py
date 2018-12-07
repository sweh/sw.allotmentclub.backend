"""Add heliosdata

Revision ID: 5baeb56d1864
Revises: 74c2dd192dae
Create Date: 2018-12-07 09:28:51.403560

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5baeb56d1864'
down_revision = '74c2dd192dae'


def upgrade():
    op.create_table(
        'dashboarddata',
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), server_default=sa.text('now()'),
                  nullable=False),
        sa.Column('luefterstufe', sa.Integer(), nullable=False),
        sa.Column('luefter_percent', sa.Integer(), nullable=False),
        sa.Column('luefter_abluft_feuchte', sa.Integer(), nullable=False),
        sa.Column('luefter_aussenluft', sa.Numeric(precision=3, scale=1),
                  nullable=False),
        sa.Column('luefter_zuluft', sa.Numeric(precision=3, scale=1),
                  nullable=False),
        sa.Column('luefter_fortluft', sa.Numeric(precision=3, scale=1),
                  nullable=False),
        sa.Column('luefter_abluft', sa.Numeric(precision=3, scale=1),
                  nullable=False),
        sa.Column('rotersee_temp_out_battery', sa.Integer(), nullable=True),
        sa.Column('rotersee_rain_battery', sa.Integer(), nullable=True),
        sa.Column('rotersee_out_temp', sa.Numeric(precision=3, scale=1),
                  nullable=True),
        sa.Column('rotersee_in_temp', sa.Numeric(precision=3, scale=1),
                  nullable=True),
        sa.Column('rotersee_out_humi', sa.Integer(), nullable=True),
        sa.Column('rotersee_in_humi', sa.Integer(), nullable=True),
        sa.Column('rotersee_in_co2', sa.Integer(), nullable=True),
        sa.Column('rotersee_rain', sa.Integer(), nullable=True),
        sa.Column('rotersee_rain_1', sa.Integer(), nullable=True),
        sa.Column('rotersee_rain_24', sa.Integer(), nullable=True),
        sa.Column('rotersee_out_temp_trend', sa.String(), nullable=True),
        sa.Column('wachtelberg_temp_out_battery', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_temp_in_battery', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_rain_battery', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_wind_battery', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_out_temp', sa.Numeric(precision=3, scale=1),
                  nullable=True),
        sa.Column('wachtelberg_in_temp', sa.Numeric(precision=3, scale=1),
                  nullable=True),
        sa.Column('wachtelberg_out_humi', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_in_humi', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_in_co2', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_rain', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_rain_1', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_rain_24', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_wind_strength', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_wind_angle', sa.Integer(), nullable=True),
        sa.Column('wachtelberg_out_temp_trend', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('date')
    )


def downgrade():
    op.drop_table('dashboarddata')
