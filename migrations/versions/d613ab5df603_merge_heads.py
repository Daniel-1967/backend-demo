"""merge heads

Revision ID: d613ab5df603
Revises: xxxxxxxxxxxx, e0d9ab1a8751
Create Date: 2026-01-28 17:26:23.427085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd613ab5df603'
down_revision: Union[str, Sequence[str], None] = ('xxxxxxxxxxxx', 'e0d9ab1a8751')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
