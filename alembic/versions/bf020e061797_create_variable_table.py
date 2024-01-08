"""create variable table

Revision ID: bf020e061797
Revises: e6f55c2f3003
Create Date: 2023-12-11 16:47:24.573258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision: str = 'bf020e061797'
down_revision: Union[str, None] = 'e6f55c2f3003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'variable',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('unit', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('asset_id', sa.Integer, sa.ForeignKey('asset.id')),
    )


def downgrade() -> None:
    op.drop_table('variable')
