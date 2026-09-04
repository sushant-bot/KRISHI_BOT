"""add decision result table

Revision ID: 0004_decision_results
Revises: 0003_images_ai
"""
import sqlalchemy as sa

from alembic import op

revision = "0004_decision_results"
down_revision = "0003_images_ai"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "decision_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("irrigation_priority", sa.String(length=32), nullable=True),
        sa.Column("water_stress", sa.String(length=32), nullable=True),
        sa.Column("heat_stress", sa.String(length=32), nullable=True),
        sa.Column("disease_spread_risk", sa.String(length=32), nullable=True),
        sa.Column("yield_risk", sa.String(length=32), nullable=True),
        sa.Column("farm_health_score", sa.Integer(), nullable=True),
        sa.Column("advisory", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_decision_results_zone_id", "decision_results", ["zone_id"])


def downgrade() -> None:
    op.drop_index("ix_decision_results_zone_id", table_name="decision_results")
    op.drop_table("decision_results")
