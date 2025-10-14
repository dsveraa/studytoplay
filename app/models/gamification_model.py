from sqlalchemy import Column, Integer, String, Float, ForeignKey
from .. import db


class Incentivos(db.Model):
    __tablename__ = "incentivos"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), nullable=False)
    condicion = Column(String, nullable=False)
    monto = Column(Float)
    nota = Column(String)


class Restricciones(db.Model):
    __tablename__ = "restricciones"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), nullable=False)
    restriccion = Column(String, nullable=False)
