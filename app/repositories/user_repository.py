from app.models.users_model import Rol
from .. import db
from app.models import Usuario

class UserRepository:
    @staticmethod
    def get_by_email(email):
        return Usuario.query.filter_by(correo=email).first()
    
    @staticmethod
    def get_by_id(id):
        return Usuario.query.filter_by(id=id).first()
    
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
    def get_all_roles():
       return Rol.query.order_by(Rol.id).all()
    
    @staticmethod
    def create_user(name, email, password_hash, role_obj):
        return Usuario(nombre=name, correo=email, contrasena=password_hash, rol=role_obj)
    
    @staticmethod
    def set_default_roles():
        student = Rol(nombre='student')
        supervisor = Rol(nombre='supervisor')
        return [student, supervisor]

    @staticmethod
    def add(obj):
        if type(obj) == list:
            db.session.add_all(obj)
            return
        db.session.add(obj)
    
    @staticmethod
    def commit():
        db.session.commit()