"""Automatic ingestion work queue and local sources without fabricated URLs."""
from alembic import op
import sqlalchemy as sa
revision = 'c09d20260909'
down_revision = 'b72e9104c301'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('sources') as batch:
        batch.alter_column('original_url', existing_type=sa.Text(), nullable=True)
    op.create_table('document_jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('owner_id', sa.String(32), nullable=False),
        sa.Column('input_kind', sa.String(16), nullable=False),
        sa.Column('input_value', sa.Text(), nullable=False),
        sa.Column('status', sa.String(32), nullable=False),
        sa.Column('manifest_key', sa.Text()), sa.Column('result_key', sa.Text()),
        sa.Column('markdown_key', sa.Text()), sa.Column('error', sa.Text()),
        sa.Column('recorded_at', sa.String(40), nullable=False),
        sa.Column('recorded_at_epoch_ms', sa.BigInteger(), nullable=False))
    op.create_index('ix_document_jobs_owner_id','document_jobs',['owner_id'])
    op.create_index('ix_document_jobs_status','document_jobs',['status'])

def downgrade():
    raise RuntimeError('Forward-only: preserve archived input and processing history')
