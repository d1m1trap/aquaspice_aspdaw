"""create asset table

Revision ID: e6f55c2f3003
Revises: f11c37be6fe8
Create Date: 2023-12-11 16:46:11.861457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision: str = 'e6f55c2f3003'
down_revision: Union[str, None] = 'f11c37be6fe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'asset',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('location', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('process_id', sa.Integer, sa.ForeignKey('process.id')),
    )


def downgrade() -> None:
    op.drop_table('asset')
