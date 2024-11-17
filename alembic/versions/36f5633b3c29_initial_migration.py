"""Initial migration

Revision ID: 36f5633b3c29
Revises: b1d4c17e226a
Create Date: 2024-11-17 21:43:56.569115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36f5633b3c29'
down_revision: Union[str, None] = 'b1d4c17e226a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('scheduled_addresses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('municipality', sa.String(length=100), nullable=False),
    sa.Column('street', sa.String(length=100), nullable=False),
    sa.Column('settlement', sa.String(length=100), nullable=True),
    sa.Column('house_range', sa.String(length=100), nullable=False),
    sa.Column('time_range', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduled_addresses_id'), 'scheduled_addresses', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('telegram_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('is_bot', sa.Boolean(), nullable=True),
    sa.Column('language_code', sa.String(length=4), nullable=False),
    sa.Column('notified_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('addresses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_address', sa.String(length=100), nullable=False),
    sa.Column('area', sa.String(length=100), nullable=False),
    sa.Column('street', sa.String(length=100), nullable=False),
    sa.Column('house_number', sa.String(length=100), nullable=False),
    sa.Column('confirmed_geolocation', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_addresses_id'), 'addresses', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_addresses_id'), table_name='addresses')
    op.drop_table('addresses')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_scheduled_addresses_id'), table_name='scheduled_addresses')
    op.drop_table('scheduled_addresses')
    # ### end Alembic commands ###