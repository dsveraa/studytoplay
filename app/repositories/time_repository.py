from sqlalchemy import desc
from app.models.tiempo_model import AcumulacionTiempo, Tiempo, Uso
from .. import db


class TimeRepository:
    @staticmethod
    def get_time_object(user_id):
        return Tiempo.query.filter_by(usuario_id=user_id).first()
    
    @staticmethod
    def time_init(id):
        return Tiempo(usuario_id=id, tiempo=0)
    
    @staticmethod
    def add(query):
        db.session.add(query)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def get_use_obj(user_id, limit=10):
        return Uso.query.filter_by(usuario_id=user_id).order_by(desc(Uso.id)).limit(limit).all()
    
    @staticmethod
    def get_time_obj_by_user_id(user_id):
        return Tiempo.query.filter_by(usuario_id=user_id).first()
    
    @staticmethod
    def get_time_accumulation_by_user_id(user_id):
        return AcumulacionTiempo.query.filter_by(usuario_id=user_id).first()
    
    @staticmethod
    def create_time(user_id, time):
        new_time = Tiempo(usuario_id=user_id, tiempo=time)
        db.session.add(new_time)

    @staticmethod
    def create_acc_time(user_id, time):
        new_time = AcumulacionTiempo(usuario_id=user_id, cantidad=time)
        db.session.add(new_time)

    @staticmethod
    def get_sorted_time_uses_list(user_id, limit):
        return Uso.query.filter_by(usuario_id=user_id).order_by(desc(Uso.id)).limit(limit).all()
    
    @staticmethod
    def set_new_use(user_id, start_date, end_date, activity, remaining_time):
        return Uso(
            usuario_id=user_id,
            fecha_inicio=start_date,
            fecha_fin=end_date,
            actividad=activity or "Not specified",
            remaining_time=remaining_time
        )
