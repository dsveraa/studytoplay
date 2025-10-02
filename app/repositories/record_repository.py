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