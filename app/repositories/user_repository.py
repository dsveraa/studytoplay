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
    def check_role(user_id, name):
        return Usuario.query.join(Rol).filter(Usuario.id == user_id, Rol.nombre == name).first()
    
    @staticmethod
    def get_role_obj_by_name(name):
        return Rol.query.filter_by(nombre=name).first()
    
    @staticmethod
    def create_user(name, email, password_hash, role_obj):
        return Usuario(nombre=name, correo=email, contrasena=password_hash, rol=role_obj)
    
    @staticmethod
    def add(new_user):
        db.session.add(new_user)
    
    @staticmethod
    def commit():
        db.session.commit()