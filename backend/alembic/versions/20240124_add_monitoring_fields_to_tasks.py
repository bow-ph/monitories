"""add monitoring fields to tasks

Revision ID: 20240124_add_monitoring
Revises: 20240124_add_priority
Create Date: 2024-01-24 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20240124_add_monitoring'
down_revision: Union[str, None] = '20240124_add_priority'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('finding_type', sa.String(), nullable=True))
    op.add_column('tasks', sa.Column('technical_details', sa.JSON(), nullable=True))
    op.add_column('tasks', sa.Column('risks', sa.JSON(), nullable=True))
    op.add_column('tasks', sa.Column('severity', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'finding_type')
    op.drop_column('tasks', 'technical_details')
    op.drop_column('tasks', 'risks')
    op.drop_column('tasks', 'severity')
