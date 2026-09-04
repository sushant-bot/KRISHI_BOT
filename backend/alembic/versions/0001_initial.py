"""create phase 1 tables

Revision ID: 0001_initial
Revises:
"""
import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "zones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("farm_id", "code", name="uq_zone_farm_code"),
    )
    op.create_index("ix_zones_farm_id", "zones", ["farm_id"])
    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("soil_moisture", sa.Float(), nullable=False),
        sa.Column("soil_temperature", sa.Float(), nullable=False),
        sa.Column("light_intensity", sa.Float(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sensor_readings_zone_id", "sensor_readings", ["zone_id"])
    op.create_index(
        "ix_sensor_readings_zone_timestamp", "sensor_readings", ["zone_id", "timestamp"]
    )


def downgrade() -> None:
    op.drop_index("ix_sensor_readings_zone_timestamp", table_name="sensor_readings")
    op.drop_index("ix_sensor_readings_zone_id", table_name="sensor_readings")
    op.drop_table("sensor_readings")
    op.drop_index("ix_zones_farm_id", table_name="zones")
    op.drop_table("zones")
    op.drop_table("farms")
