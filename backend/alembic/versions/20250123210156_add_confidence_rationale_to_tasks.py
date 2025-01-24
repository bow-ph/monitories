"""add confidence rationale to tasks

Revision ID: 6b546a2b3aeb
Revises: 
Create Date: 2025-01-23 21:01:56.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfe54b3b5c15'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('confidence_rationale', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'confidence_rationale')
