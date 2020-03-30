"""User status

Revision ID: 339a6b145e56
Revises: 9f52309f0d44
Create Date: 2020-03-26 11:53:32.044767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '339a6b145e56'
down_revision = '9f52309f0d44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('status', sa.Enum('ENABLED', 'DELETED', 'PENDING_APPROVAL', name='UserStatusEnumType'), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'status')
    # ### end Alembic commands ###
