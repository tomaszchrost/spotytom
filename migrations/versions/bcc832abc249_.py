"""empty message

Revision ID: bcc832abc249
Revises: 5915a4c60344
Create Date: 2021-08-28 21:15:41.185090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcc832abc249'
down_revision = '5915a4c60344'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('lastfm_username', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'lastfm_username')
    # ### end Alembic commands ###
