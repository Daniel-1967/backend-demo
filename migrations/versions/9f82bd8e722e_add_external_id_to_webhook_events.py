"""add external_id to webhook_events

Revision ID: 9f82bd8e722e
Revises: 6fcd3dec7cc8
Create Date: 2026-01-26 15:02:43.917353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f82bd8e722e'
down_revision: Union[str, Sequence[str], None] = '6fcd3dec7cc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
