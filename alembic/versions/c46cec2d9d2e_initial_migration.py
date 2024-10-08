"""Initial migration

Revision ID: c46cec2d9d2e
Revises: 
Create Date: 2024-09-20 13:02:21.157573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c46cec2d9d2e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('scheduled_addresses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('municipality', sa.String(length=100), nullable=False),
    sa.Column('street', sa.String(length=100), nullable=False),
    sa.Column('house_range', sa.String(length=100), nullable=False),
    sa.Column('time_range', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduled_addresses_id'), 'scheduled_addresses', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_scheduled_addresses_id'), table_name='scheduled_addresses')
    op.drop_table('scheduled_addresses')
    # ### end Alembic commands ###
