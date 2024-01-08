"""create process table

Revision ID: f11c37be6fe8
Revises: 21f19572e1b8
Create Date: 2023-12-11 16:43:38.377235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision: str = 'f11c37be6fe8'
down_revision: Union[str, None] = '21f19572e1b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'process',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('location', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('pilot_id', sa.Integer, sa.ForeignKey('pilot.id')),
    )


def downgrade() -> None:
    op.drop_table('process')
