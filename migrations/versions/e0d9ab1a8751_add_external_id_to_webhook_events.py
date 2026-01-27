"""add external_id to webhook_events

Revision ID: e0d9ab1a8751
Revises: 9f82bd8e722e
Create Date: 2026-01-26 15:06:30.084753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0d9ab1a8751'
down_revision: Union[str, Sequence[str], None] = '9f82bd8e722e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("webhook_events", sa.Column("external_id", sa.String(length=128), nullable=True))
    op.create_index("ix_webhook_events_external_id", "webhook_events", ["external_id"])

def downgrade() -> None:
    op.drop_index("ix_webhook_events_external_id", table_name="webhook_events")
    op.drop_column("webhook_events", "external_id")
