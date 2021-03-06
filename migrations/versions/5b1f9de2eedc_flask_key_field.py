"""flask key field

Revision ID: 5b1f9de2eedc
Revises: 79a822c0d158
Create Date: 2020-10-28 20:20:53.325016

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5b1f9de2eedc'
down_revision = '79a822c0d158'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('lastfm_key', sa.String(length=128), nullable=True))
    op.drop_column('user', 'spotify_username')
    op.drop_column('user', 'lastfm_username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('lastfm_username', mysql.VARCHAR(length=128), nullable=True))
    op.add_column('user', sa.Column('spotify_username', mysql.VARCHAR(length=128), nullable=True))
    op.drop_column('user', 'lastfm_key')
    # ### end Alembic commands ###
