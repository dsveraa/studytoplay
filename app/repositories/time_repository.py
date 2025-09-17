from app.models.tiempo_model import Tiempo
from .. import db


class TimeRepository:
    @staticmethod
    def get_time_object(id):
        return Tiempo.query.filter_by(usuario_id=id).first()
    
    @staticmethod
    def time_init(id):
        return Tiempo(usuario_id=id, tiempo=0)
    
    @staticmethod
    def commit(query):
        db.session.add(query)
        db.session.commit()

    