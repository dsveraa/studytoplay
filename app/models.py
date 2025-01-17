from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import db

class Usuario(db.Model):
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    contrasena = Column(String(200), nullable=False)
    
    def __repr__(self):
        return f'<Usuario {self.nombre}>'

class Tiempo(db.Model):
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    tiempo = Column(Float, default=0.0)
    usuario = relationship('Usuario', backref='tiempos', lazy=True)
    
    def __repr__(self):
        return f'<Tiempo {self.id} - Usuario {self.usuario.nombre}>'

class Estudio(db.Model):
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    resumen = Column(Text, nullable=False)
    usuario = relationship('Usuario', backref='estudios', lazy=True)
    
    def __repr__(self):
        return f'<Estudio {self.id} - Usuario {self.usuario.nombre}>'

class Uso(db.Model):
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    usuario = relationship('Usuario', backref='usos', lazy=True)
    
    def __repr__(self):
        return f'<Uso {self.id} - Usuario {self.usuario.nombre}>'