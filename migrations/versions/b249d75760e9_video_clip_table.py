"""video_clip table

Revision ID: b249d75760e9
Revises: 2d1f40a09897
Create Date: 2023-08-17 11:47:59.172458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b249d75760e9'
down_revision = '2d1f40a09897'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('video_clips',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_video_clips_name'), 'video_clips', ['name'], unique=False)
    op.add_column('render_hosts', sa.Column('record_date', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('render_hosts', 'record_date')
    op.drop_index(op.f('ix_video_clips_name'), table_name='video_clips')
    op.drop_table('video_clips')
    # ### end Alembic commands ###
