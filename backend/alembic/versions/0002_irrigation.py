"""add irrigation and alert tables

Revision ID: 0002_irrigation
Revises: 0001_initial
"""
import sqlalchemy as sa

from alembic import op

revision = "0002_irrigation"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "irrigation_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("command", sa.String(length=16), nullable=False),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_water_liters", sa.Float(), nullable=True),
        sa.Column("water_delivered_liters", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("fault_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_irrigation_events_zone_id", "irrigation_events", ["zone_id"])
    op.create_index("ix_irrigation_events_status", "irrigation_events", ["status"])

    op.create_table(
        "water_flow_readings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("irrigation_event_id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("flow_rate", sa.Float(), nullable=False),
        sa.Column("water_delivered_liters", sa.Float(), nullable=False),
        sa.Column("pump_status", sa.String(length=8), nullable=False),
        sa.ForeignKeyConstraint(
            ["irrigation_event_id"], ["irrigation_events.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_water_flow_readings_irrigation_event_id",
        "water_flow_readings",
        ["irrigation_event_id"],
    )
    op.create_index("ix_water_flow_readings_zone_id", "water_flow_readings", ["zone_id"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_index("ix_water_flow_readings_zone_id", table_name="water_flow_readings")
    op.drop_index(
        "ix_water_flow_readings_irrigation_event_id", table_name="water_flow_readings"
    )
    op.drop_table("water_flow_readings")
    op.drop_index("ix_irrigation_events_status", table_name="irrigation_events")
    op.drop_index("ix_irrigation_events_zone_id", table_name="irrigation_events")
    op.drop_table("irrigation_events")
