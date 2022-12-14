"""add new columns for user

Revision ID: 11061417c577
Revises: 4af41574334d
Create Date: 2022-11-07 00:08:19.812092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11061417c577'
down_revision = '4af41574334d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.String(length=120), nullable=True))
    op.add_column('user', sa.Column('create_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'create_time')
    op.drop_column('user', 'about_me')
    # ### end Alembic commands ###
