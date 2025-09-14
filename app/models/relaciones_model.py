from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .. import db
from datetime import datetime, timezone


class SupervisorEstudiante(db.Model):
    __tablename__ = 'supervisor_estudiante'
    __table_args__ = (
        UniqueConstraint('supervisor_id', 'estudiante_id', name='unique_supervisor_estudiante'),
    )

    id = Column(Integer, primary_key=True)

    supervisor_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"))
    estudiante_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"))

    supervisor = relationship('Usuario', foreign_keys=[supervisor_id], backref='estudiantes_asignados')
    estudiante = relationship('Usuario', foreign_keys=[estudiante_id], backref='supervisores_asignados')


class SolicitudVinculacion(db.Model):
    __tablename__ = 'solicitud_vinculacion'

    id = Column(Integer, primary_key=True)

    supervisor_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"))
    estudiante_id = Column(Integer, ForeignKey('usuarios.id', ondelete="CASCADE"))
    estado = Column(String, default='pendiente')
    fecha_solicitud = Column(DateTime, default=datetime.now(timezone.utc))

    supervisor = relationship('Usuario', foreign_keys=[supervisor_id], backref='solicitudes_enviadas')
    estudiante = relationship('Usuario', foreign_keys=[estudiante_id], backref='solicitudes_recibidas')

    def to_dict(self):
        d = self.__dict__.copy()
        d.pop('_sa_instance_state', None)
        return d
