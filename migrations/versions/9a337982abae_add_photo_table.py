"""Add photo table

Revision ID: 9a337982abae
Revises: 738edf08693c
Create Date: 2022-07-18 11:03:04.059799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a337982abae'
down_revision = '738edf08693c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'photos',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tg_user_id', sa.String(50), nullable=False),
        sa.Column('photo', sa.LargeBinary(length=(2**32)-1), nullable=False)),     
    op.create_index('ix_photos_tg_user_id', 'photos', ['tg_user_id'], unique=False),


def downgrade() -> None:
    op.drop_index('ix_photos_tg_user_id', table_name='photos')
    op.drop_table('photos')
