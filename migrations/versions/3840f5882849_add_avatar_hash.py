"""add avatar_hash

Revision ID: 3840f5882849
Revises: 81823e807c41
Create Date: 2017-03-01 22:44:44.396180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3840f5882849'
down_revision = '81823e807c41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_hash', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_hash')
    # ### end Alembic commands ###
