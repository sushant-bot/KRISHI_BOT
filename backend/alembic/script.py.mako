"""${message}"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

${up_revision_cmd}
${down_revision_cmd}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
