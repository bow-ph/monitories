import uuid
from datetime import datetime

migration_template = f"""\"\"\"add confidence rationale to tasks

Revision ID: {uuid.uuid4().hex[:12]}
Revises: 
Create Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-6]}

\"\"\"
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '{uuid.uuid4().hex[:12]}'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('confidence_rationale', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'confidence_rationale')
"""

timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
filename = f"alembic/versions/{timestamp}_add_confidence_rationale_to_tasks.py"

with open(filename, 'w') as f:
    f.write(migration_template)
