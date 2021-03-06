"""empty message

Revision ID: 04205e193be1
Revises: 6691e9f3ee37
Create Date: 2020-08-19 16:18:56.221869

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '04205e193be1'
down_revision = '6691e9f3ee37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('api_token', sa.String(length=200), nullable=True))
    op.alter_column('user', 'authentication_type',
               existing_type=mysql.ENUM('LDAP', 'INTERNAL', 'AD', collation='utf8_unicode_ci'),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'authentication_type',
               existing_type=mysql.ENUM('LDAP', 'INTERNAL', 'AD', collation='utf8_unicode_ci'),
               nullable=False)
    op.drop_column('user', 'api_token')
