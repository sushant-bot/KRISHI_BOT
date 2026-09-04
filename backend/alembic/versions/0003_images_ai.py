"""add crop images and AI result tables

Revision ID: 0003_images_ai
Revises: 0002_irrigation
"""
import sqlalchemy as sa

from alembic import op

revision = "0003_images_ai"
down_revision = "0002_irrigation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(length=1024), nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crop_images_farm_id", "crop_images", ["farm_id"])
    op.create_index("ix_crop_images_zone_id", "crop_images", ["zone_id"])

    op.create_table(
        "ai_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("zone_id", sa.Integer(), nullable=False),
        sa.Column("crop_health", sa.String(length=64), nullable=True),
        sa.Column("disease", sa.String(length=128), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("growth_stage", sa.String(length=64), nullable=True),
        sa.Column("provider", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["image_id"], ["crop_images.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_results_image_id", "ai_results", ["image_id"])
    op.create_index("ix_ai_results_zone_id", "ai_results", ["zone_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_results_zone_id", table_name="ai_results")
    op.drop_index("ix_ai_results_image_id", table_name="ai_results")
    op.drop_table("ai_results")
    op.drop_index("ix_crop_images_zone_id", table_name="crop_images")
    op.drop_index("ix_crop_images_farm_id", table_name="crop_images")
    op.drop_table("crop_images")
