from app.models.relations_model import SupervisorEstudiante
from .. import db


class SupervisorStudentRepository:
    @staticmethod
    def get_relation(supervisor_id, student_id):
        return  (
            db.session.query(SupervisorEstudiante)
            .filter_by(supervisor_id=supervisor_id, estudiante_id=student_id)
            .scalar()
        )
