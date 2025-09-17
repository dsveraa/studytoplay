from app.repositories.time_repository import TimeRepository
from .. import db


class UserTime:    
    def __init__(self, user_id: int):
        self.id = user_id
        self.time_obj = TimeRepository.get_time_object(user_id)

    def get_time(self):
        if not self.time_obj:
            query = TimeRepository.time_init(self.id)
            TimeRepository.commit(query)
            return TimeRepository.get_time_object(self.id).tiempo
        return self.time_obj.tiempo
              
    def manage_time(self, action, time):
        options = ['add', 'substract']

        if action not in options:
            return "Invalid option"

        if action == 'add':
            self.time_obj.tiempo += time
        else:
            self.time_obj.tiempo -= time

        db.session.commit()
        return self.time_obj.tiempo

    def reset_time(self):
        self.time_obj.tiempo = 0
        db.session.commit()
        return self.time_obj.tiempo
    