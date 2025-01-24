from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import db

'''
TIP: Al renombrar una tabla, no es necesario migrar las claves foraneas, es decir, no debe haber instrucciones de modificación en los archivos de migración, solo instrucciones para renombrar. La base de datos mantendrá las relaciones entre las tablas y solo hay que actualizar los modelos de SQLAlchemy.

Ej. Modelo: 

class Usuario():
    __tablename__ = 'usuario' -> __tablename__ = 'usuarios'

class Estudio():
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False) -> 'usuarios.id'


Ej. Migración:

def upgrade():
    op.rename_table('usuario', 'usuarios')

def downgrade():
    op.rename_table('usuarios', 'usuario')

'''

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    contrasena = Column(String(200), nullable=False)

    estudios = relationship('Estudio', back_populates='usuario')
    tiempos = relationship('Tiempo', back_populates='usuario')
    usos = relationship('Uso', back_populates='usuario')
    
class Tiempo(db.Model):
    __tablename__ = 'tiempos'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tiempo = Column(Float, default=0.0)
    
    usuario = relationship('Usuario', back_populates='tiempo')
    
class Estudio(db.Model):
    __tablename__ = 'estudios'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    resumen = Column(Text, nullable=False)
    asignatura_id = Column(Integer, ForeignKey('asignaturas.id'), nullable=True)

    usuario = relationship('Usuario', back_populates='estudio')
    asignatura = relationship('Asignatura', back_populates='estudio')
    
class Uso(db.Model):
    __tablename__ = 'usos'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    
    usuario = relationship('Usuario', back_populates='uso')

class Asignatura(db.Model):
    __tablename__ = 'asignaturas'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)

    estudio = relationship('Estudio', back_populates='asignatura')