from flask import session
from app.models.users_model import Rol
from app.repositories.user_repository import UserRepository
from app.repositories.user_status_repository import UserStatusRepository


class UserService:
    @staticmethod
    def get_from_email(email):
        user = UserRepository.get_by_email(email)
        
        if not user:
            raise ValueError('The user does not exist')
        
        return user

    @staticmethod
    def get_id_from_email(email):
        user = UserRepository.get_by_email(email)
        
        if not user:
            raise ValueError('The user does not exist')
        
        return user.id

    @staticmethod
    def get_all_roles():
        role_obj = Rol.query.order_by(Rol.id).all()
        return [{'id': role.id, 'nombre': role.nombre} for role in role_obj]
    
    @staticmethod
    def get_id_from_session():
        return session['usuario_id']
    
    @staticmethod
    def check_role(user_id, name):
        return UserRepository.check_role(user_id, name)
    

class UserStatusService:
    @staticmethod
    def switch_status(user_id, status: str):
        current_status = UserStatusRepository.get_status_object(user_id)

        if current_status:
            current_status.estado = status
        else:
            current_status = UserStatusRepository.set_new_status(user_id, status)
            UserStatusRepository.add_new_status(current_status)

        UserStatusRepository.commit()
        return current_status
    