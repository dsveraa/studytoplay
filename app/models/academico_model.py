from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from .. import db


class Estudio(db.Model):
    __tablename__ = 'estudios'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    resumen = Column(Text, nullable=False)
    asignatura_id = Column(Integer, ForeignKey('asignaturas.id'), nullable=True)

    usuario = relationship('Usuario', back_populates='estudios')
    asignatura = relationship('Asignatura', back_populates='estudio')


class Asignatura(db.Model):
    __tablename__ = 'asignaturas'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"))

    estudio = relationship('Estudio', back_populates='asignatura')
    registro_nota = relationship('RegistroNotas', back_populates='asignatura')


class RegistroNotas(db.Model):
    __tablename__ = 'registro_notas'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), nullable=False)
    asignatura_id = Column(Integer, ForeignKey('asignaturas.id'), nullable=False)
    tema = Column(String, nullable=False)
    nota = Column(Float, nullable=False)
    fecha = Column(DateTime, nullable=False)
    estado = Column(Boolean, default=False, nullable=False)

    asignatura = relationship('Asignatura', back_populates='registro_nota')
