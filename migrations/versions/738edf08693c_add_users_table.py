"""Add users table

Revision ID: 738edf08693c
Revises: 710b5d5b7e37
Create Date: 2022-07-18 11:02:11.606416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '738edf08693c'
down_revision = '710b5d5b7e37'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tg_user_id', sa.String(50), nullable=False),
        sa.Column('clip_name', sa.String(50), nullable=False),
        sa.Column('record_date', sa.DateTime, nullable=False),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('render_host', sa.String(50), nullable=True),
        sa.Column('render_time', sa.Integer(), nullable=True))
    op.create_index('ix_users_tg_user_id', 'users', ['tg_user_id'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_users_tg_user_id', table_name='users')
    op.drop_table('users')    
