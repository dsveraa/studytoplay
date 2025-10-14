from werkzeug.security import generate_password_hash
from app.models.notifications_model import NuevaNotificacion
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app import db


class SignUpService:
    @staticmethod
    def signup(name, email, password, repeat_password, role):
        errors = []
        if UserRepository.get_by_email(email):
            errors.append(f"E-mail <b>{email}</b> is already used.")
        if password != repeat_password:
            errors.append("Passwords doesn't match, try again.")

        if errors:
            raise ValueError(errors)
        
        if role == "1":
            role_obj = UserRepository.get_role_obj_by_name('student')
        
        else:
            role_obj = UserRepository.get_role_obj_by_name('supervisor')

        password_hash = generate_password_hash(password)
        new_user = UserRepository.create_user(name, email, password_hash, role_obj)
        UserRepository.add(new_user)
        UserRepository.commit()

        user_id = UserService.get_id_from_email(email)
        default = NuevaNotificacion(usuario_id=user_id, estado=False)
        db.session.add(default)
        db.session.commit()