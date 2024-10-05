"""Added settlement field to ScheduledAddress

Revision ID: b1d4c17e226a
Revises: c46cec2d9d2e
Create Date: 2024-09-20 14:53:01.860010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1d4c17e226a'
down_revision: Union[str, None] = 'c46cec2d9d2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scheduled_addresses', sa.Column('settlement', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scheduled_addresses', 'settlement')
    # ### end Alembic commands ###
