from app.models.users_model import Rol
from .. import db
from app.models import Usuario

class UserRepository:
    @staticmethod
    def get_by_email(email):
        return Usuario.query.filter_by(correo=email).first()
    
    @staticmethod
    def get_id_by_email(email):
        return db.session.query(Usuario.id).filter_by(correo=email).scalar()
        
    @staticmethod
    def get_email_by_id(id):
        user = Usuario.query.filter_by(id=id).first()
        return user.correo
    
    @staticmethod
    def check_supervisor(user_id, name):
        return Usuario.query.join(Rol).filter(Usuario.id == user_id, Rol.nombre == name).first()