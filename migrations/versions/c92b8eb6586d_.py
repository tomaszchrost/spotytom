"""empty message

Revision ID: c92b8eb6586d
Revises: 38931f6020d4
Create Date: 2020-11-15 17:17:37.642173

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c92b8eb6586d'
down_revision = '38931f6020d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('lastfm_name', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'lastfm_name')
    # ### end Alembic commands ###
