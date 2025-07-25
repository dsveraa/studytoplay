"""tabla solicitud vinculacion

Revision ID: 337e582a8838
Revises: 8f92d8b49e8b
Create Date: 2025-04-08 14:45:03.583723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '337e582a8838'
down_revision = '8f92d8b49e8b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('solicitud_vinculacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('supervisor_id', sa.Integer(), nullable=True),
    sa.Column('estudiante_id', sa.Integer(), nullable=True),
    sa.Column('estado', sa.String(), nullable=True),
    sa.Column('fecha_solicitud', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['estudiante_id'], ['usuarios.id'], ),
    sa.ForeignKeyConstraint(['supervisor_id'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('solicitud_vinculacion')
    # ### end Alembic commands ###
