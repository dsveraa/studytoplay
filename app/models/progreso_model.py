from sqlalchemy import Column, Integer, String, ForeignKey
from .. import db

class Nivel(db.Model):
    __tablename__ = "niveles"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    nivel = Column(Integer)


class Trofeo(db.Model):
    __tablename__ = "trofeos"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    cantidad = Column(Integer)


class Premio(db.Model):
    __tablename__ = "premios"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    descripcion = Column(String(100))


class Estrella(db.Model):
    __tablename__ = 'estrellas'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    cantidad = Column(Integer)
