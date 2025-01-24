"""Cambiar nombres de tablas a plural

Revision ID: f069f19cc617
Revises: 6f57a273a612
Create Date: 2025-01-24 14:21:24.348136

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f069f19cc617'
down_revision = '6f57a273a612'
branch_labels = None
depends_on = None


from alembic import op

def upgrade():
    op.rename_table('usuario', 'usuarios')
    op.rename_table('tiempo', 'tiempos')
    op.rename_table('estudio', 'estudios')
    op.rename_table('uso', 'usos')
    op.rename_table('asignatura', 'asignaturas')

def downgrade():
    op.rename_table('usuarios', 'usuario')
    op.rename_table('tiempos', 'tiempo')
    op.rename_table('estudios', 'estudio')
    op.rename_table('usos', 'uso')
    op.rename_table('asignaturas', 'asignatura')

