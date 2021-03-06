"""empty message

Revision ID: 1d8898fd3f7e
Revises: c92b8eb6586d
Create Date: 2020-11-15 19:38:10.169768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d8898fd3f7e'
down_revision = 'c92b8eb6586d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('updating_playlist', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'updating_playlist')
    # ### end Alembic commands ###
