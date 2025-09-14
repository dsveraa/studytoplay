from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, text, Float
from sqlalchemy.orm import relationship
from .. import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    contrasena = Column(String(200), nullable=False)
    rol_id = Column(Integer, ForeignKey('roles.id'))
    
    estudios = relationship('Estudio', back_populates='usuario', passive_deletes=True)
    tiempo = relationship('Tiempo', back_populates='usuario', uselist=False, passive_deletes=True)
    usos = relationship('Uso', back_populates='usuario', passive_deletes=True)

    niveles = relationship('Nivel', backref='usuario', passive_deletes=True)
    trofeos = relationship('Trofeo', backref='usuario', passive_deletes=True)
    acumulacion_tiempos = relationship('AcumulacionTiempo', backref='usuario', passive_deletes=True)
    estrellas = relationship('Estrella', backref='usuario', passive_deletes=True)
    asignaturas = relationship('Asignatura', backref='usuario', passive_deletes=True)
    rol = relationship('Rol', backref='usuario', passive_deletes=True)
    incentivos = relationship("Incentivos", backref="usuario", passive_deletes=True)
    restricciones = relationship("Restricciones", backref="usuario", passive_deletes=True)


class Rol(db.Model):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    nombre = Column(String)


class EstadoUsuario(db.Model):
    __tablename__ = 'estado_usuario'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), unique=True)
    estado = Column(String, default='idle')


class Settings(db.Model):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), nullable=False, unique=True)
    incentivo_notas = Column(Boolean, server_default=text("false"), nullable=False)
    pais_id = Column(Integer, ForeignKey("pais.id"), server_default=text("1"), nullable=False)
    trofeo = Column(String, server_default=text("'Unconditional love &#10084;&#65039;'"), nullable=False)
    extra_time = Column(Integer, server_default="1800000")
    time_ratio = Column(Float, server_default="1.0")

    pais = relationship("Pais", backref="settings")
    usuario = relationship("Usuario", backref="settings")
