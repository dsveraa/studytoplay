from .. import db
from app.models import EstadoUsuario

class UserStatusRepository:
    @staticmethod
    def get_status_object(user_id):
        return EstadoUsuario.query.filter_by(usuario_id=user_id).first()
    
    @staticmethod
    def set_new_status(user_id, status):
        return EstadoUsuario(usuario_id=user_id, estado=status)
    
    @staticmethod
    def add_new_status(new_status):
        db.session.add(new_status)
    
    @staticmethod
    def commit():
        db.session.commit()