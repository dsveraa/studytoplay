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
