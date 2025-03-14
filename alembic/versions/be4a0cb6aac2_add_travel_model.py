"""add Travel model

Revision ID: be4a0cb6aac2
Revises: 6b7242cb4fab
Create Date: 2024-03-24 20:35:23.446277

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'be4a0cb6aac2'
down_revision = '6b7242cb4fab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('travels',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('title', sa.Text(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('owner_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('title', 'owner_id', name='_travel_uc')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('travels')
    # ### end Alembic commands ###
