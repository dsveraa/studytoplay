from sqlalchemy import Column, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .. import db


class Tiempo(db.Model):
    __tablename__ = 'tiempos'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, unique=True)
    tiempo = Column(Float, default=0.0)
    
    usuario = relationship('Usuario', back_populates='tiempo')
    
    
class Uso(db.Model):
    __tablename__ = 'usos'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    actividad = Column(Text, nullable=False, default="")
    
    usuario = relationship('Usuario', back_populates='usos')


class AcumulacionTiempo(db.Model):
    __tablename__ = "acumulacion_tiempos"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    cantidad = Column(Float)
