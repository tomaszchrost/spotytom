"""remove email

Revision ID: 38931f6020d4
Revises: 5b1f9de2eedc
Create Date: 2020-10-28 20:31:09.756585

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '38931f6020d4'
down_revision = '5b1f9de2eedc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_email', table_name='user')
    op.drop_column('user', 'email')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email', mysql.VARCHAR(length=120), nullable=True))
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    # ### end Alembic commands ###
