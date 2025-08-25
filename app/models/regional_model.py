from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .. import db


class Monedas(db.Model):
    __tablename__ = "monedas"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    simbolo_id = Column(Integer, ForeignKey("simbolos.id"), nullable=False)

    simbolo = relationship("Simbolos", backref="monedas")


class Simbolos(db.Model):
    __tablename__ = "simbolos"
    
    id = Column(Integer, primary_key=True)
    simbolo = Column(String, nullable=False)


class Pais(db.Model):
    __tablename__ = "pais"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    moneda_id = Column(ForeignKey("monedas.id"))

    moneda = relationship("Monedas", backref="pais")
