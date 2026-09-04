"""response_events composite index for target + effective time

Revision ID: a1d94c07f2b6
Revises: e06e20237418
Create Date: 2026-09-04 16:40:00.000000

The single-column target_id index is dropped because the new composite
index serves target-only lookups through its leftmost prefix.
"""

from typing import Sequence, Union

from alembic import op


revision: str = 'a1d94c07f2b6'
down_revision: Union[str, None] = 'e06e20237418'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        'ix_response_events_target_effective',
        'response_events',
        ['target_id', 'effective_at_epoch_ms'],
        unique=False,
    )
    op.drop_index(
        op.f('ix_response_events_target_id'), table_name='response_events'
    )


def downgrade() -> None:
    op.create_index(
        op.f('ix_response_events_target_id'),
        'response_events',
        ['target_id'],
        unique=False,
    )
    op.drop_index(
        'ix_response_events_target_effective', table_name='response_events'
    )
