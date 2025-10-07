from sqlalchemy import desc
from app import db
from sqlalchemy.orm import aliased

from app.models.relaciones_model import SolicitudVinculacion, SupervisorEstudiante
from app.models.users_model import Usuario


class RelationsRepository:
    @staticmethod
    def get_supervisor_student_relation(user_id):
        Supervisor = aliased(Usuario)
        Student = aliased(Usuario)
        
        return (
        db.session.query(
            Supervisor.id.label('supervisor_id'),
            Supervisor.nombre.label('supervisor'),
            SolicitudVinculacion.estudiante_id,
            Student.nombre.label('estudiante'),
            SolicitudVinculacion.estado,
            SolicitudVinculacion.fecha_solicitud
        )
        .select_from(Supervisor)
        .join(SolicitudVinculacion, Supervisor.id == SolicitudVinculacion.supervisor_id)
        .join(Student, Student.id == SolicitudVinculacion.estudiante_id)
        .filter(SolicitudVinculacion.estudiante_id == user_id)
        .order_by(desc(SolicitudVinculacion.fecha_solicitud))
        .all()
    )

    @staticmethod
    def get_link_request(request_id, student_id):
        return SolicitudVinculacion.query.filter_by(
            id=request_id, 
            estudiante_id=student_id
            ).order_by(
                desc(SolicitudVinculacion.fecha_solicitud)
                ).first()
    
    @staticmethod
    def check_existing_relationship(request):
        return SupervisorEstudiante.query.filter_by(
                supervisor_id=request.supervisor_id,
                estudiante_id=request.estudiante_id
            ).first()
    
    @staticmethod
    def create_relationship(request):
        return SupervisorEstudiante(
                    supervisor_id=request.supervisor_id,
                    estudiante_id=request.estudiante_id
                )
        
    @staticmethod
    def add(object):
        db.session.add(object)
    
    @staticmethod
    def commit():
        db.session.commit()