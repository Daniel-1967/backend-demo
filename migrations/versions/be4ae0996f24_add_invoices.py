"""add invoices

Revision ID: xxxxxxxxxxxx
Revises: 6fcd3dec7cc8
Create Date: 2026-01-xx
"""

from alembic import op
import sqlalchemy as sa

revision = "xxxxxxxxxxxx"
down_revision = "6fcd3dec7cc8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="USD"),
        sa.Column("due_date", sa.String(length=16), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_invoices_external_id", "invoices", ["external_id"])


def downgrade() -> None:
    op.drop_index("ix_invoices_external_id", table_name="invoices")
    op.drop_table("invoices")
