from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, Boolean
from .. import db
from datetime import datetime


class Notificaciones(db.Model):
    __tablename__ = 'notificaciones'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"))
    notificacion = Column(Text)
    leida = Column(Boolean, default=False)
    fecha = Column(DateTime, default=datetime.now)


class NuevaNotificacion(db.Model):
    __tablename__ = 'nuevas_notificaciones'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), unique=True)
    estado = Column(Boolean, default=False, nullable=False)
