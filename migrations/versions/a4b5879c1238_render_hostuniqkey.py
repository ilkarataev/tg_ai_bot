"""render_hostuniqkey

Revision ID: a4b5879c1238
Revises: 770baccc6d06
Create Date: 2023-08-17 18:34:42.837670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4b5879c1238'
down_revision = '770baccc6d06'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_render_hosts_render_host', table_name='render_hosts')
    op.create_index(op.f('ix_render_hosts_render_host'), 'render_hosts', ['render_host'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_render_hosts_render_host'), table_name='render_hosts')
    op.create_index('ix_render_hosts_render_host', 'render_hosts', ['render_host'], unique=False)
    # ### end Alembic commands ###
