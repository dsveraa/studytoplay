from app.models.users_model import Rol
from app.repositories.user_repository import UserRepository


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
    