from app.models.academico_model import RegistroNotas
from app import db


class AcademicRepository:
    @staticmethod
    def get_grade_by_id(record_id):
        return RegistroNotas.query.get_or_404(record_id)
    
    @staticmethod
    def set_grade_as_payed(record_id):
        record = RegistroNotas.query.get_or_404(record_id)
        record.estado = True
    
    @staticmethod
    def set_grade(user_id, subject_id, topic, grade, date):
        return RegistroNotas(
        usuario_id=user_id,
        asignatura_id=subject_id,
        tema=topic,
        nota=grade,
        fecha=date,
    )

    @staticmethod
    def add_grade(obj):
        db.session.add(obj)
    
    @staticmethod
    def commit():
        db.session.commit()