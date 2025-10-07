from sqlalchemy import desc
from app.models.relaciones_model import SolicitudVinculacion
from .. import db


class LinkRequestRepository:
    @staticmethod
    def get_status(supervisor_id, student_id):
        return (
            db.session.query(SolicitudVinculacion.estado)
            .select_from(SolicitudVinculacion)
            .filter_by(supervisor_id=supervisor_id, estudiante_id=student_id)
            .order_by(desc(SolicitudVinculacion.fecha_solicitud))
            .limit(1).scalar()
            )

    @staticmethod
    def set_query(supervisor_id, student_id):
        return SolicitudVinculacion(
                supervisor_id=supervisor_id,
                estudiante_id=student_id,
                estado='pendiente'
            )
    
    @staticmethod
    def add_link_request(query):
        db.session.add(query)

    @staticmethod
    def commit():
        db.session.commit()
        