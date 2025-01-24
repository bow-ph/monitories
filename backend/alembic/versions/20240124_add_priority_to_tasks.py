"""add priority to tasks

Revision ID: 20240124_add_priority
Revises: 20240123210156
Create Date: 2024-01-24 07:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240124_add_priority'
down_revision: Union[str, None] = '20240123210156'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('priority', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'priority')
