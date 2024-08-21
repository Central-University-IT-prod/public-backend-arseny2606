"""add TravelNote model

Revision ID: b13ff529048d
Revises: 51f66ad703c6
Create Date: 2024-03-26 01:42:42.720508

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b13ff529048d'
down_revision = '51f66ad703c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('travel_notes',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('file_id', sa.Text(), nullable=False),
                    sa.Column('file_name', sa.Text(), nullable=True),
                    sa.Column('is_public', sa.Boolean(), nullable=True),
                    sa.Column('travel_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['travel_id'], ['travels.id'], ),
                    sa.PrimaryKeyConstraint('id', 'file_id', 'travel_id'),
                    sa.UniqueConstraint('file_id', 'travel_id', name='_note_travel_uc')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('travel_notes')
    # ### end Alembic commands ###
