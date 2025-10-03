from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from app.repositories.user_repository import UserRepository


class LoginService:
    @staticmethod
    def login(email, password):
        user = UserRepository.get_by_email(email)

        if not user:
            raise ValueError("User doesn't exist.")           
        
        if not check_password_hash(user.contrasena, password):
            raise ValueError("Incorrect password.")

        session["usuario_id"] = user.id
        session["usuario_nombre"] = user.nombre

        supervisor = UserRepository.check_supervisor(user.id, 'supervisor')
        
        if supervisor:
            session["supervisor_id"] = user.id

        session.permanent = True
        