"""Append-only legacy file import ledger."""
from alembic import op
import sqlalchemy as sa

revision = "b72e9104c301"
down_revision = "a1d94c07f2b6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "legacy_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("relative_key", sa.Text(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("source_id", sa.String(32), nullable=True),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("recorded_at", sa.String(40), nullable=False),
        sa.Column("recorded_at_epoch_ms", sa.BigInteger(), nullable=False),
        sa.UniqueConstraint("relative_key", "sha256"),
    )


def downgrade():
    op.drop_table("legacy_documents")
