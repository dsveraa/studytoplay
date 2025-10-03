from sqlalchemy import desc
from app.models.academico_model import Estudio
from app import db

class RecordRepository:
    def __init__(self, id, user_id):
        self.record = Estudio.query.filter_by(id=id, usuario_id=user_id).first()
        self.resumen = self.record.resumen

    def get_study_obj(self):
        return self.record
    
    def set_summary(self, new_summary):
        self.record.resumen = new_summary
    
    def commit(self):
        db.session.commit()

    @staticmethod
    def get_list_by_activity(user_id, activity_id):
        return Estudio.query.filter_by(usuario_id=user_id, asignatura_id=activity_id).order_by(desc(Estudio.id)).all()
    
    @staticmethod
    def get_full_list(user_id, limit):
        return Estudio.query.filter_by(usuario_id=user_id).order_by(desc(Estudio.id)).limit(limit).all()
    