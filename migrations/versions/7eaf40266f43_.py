"""empty message

Revision ID: 7eaf40266f43
Revises: bcc832abc249
Create Date: 2021-08-30 17:41:07.186636

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7eaf40266f43'
down_revision = 'bcc832abc249'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('spotify_token', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'spotify_token')
    # ### end Alembic commands ###
