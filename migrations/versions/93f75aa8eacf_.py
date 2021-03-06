"""empty message

Revision ID: 93f75aa8eacf
Revises: 30ba0708e1b7
Create Date: 2020-11-29 22:00:20.116960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93f75aa8eacf'
down_revision = '30ba0708e1b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('sid', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'sid')
    # ### end Alembic commands ###
