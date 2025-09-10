from app.models import Tiempo
from .. import db


class UserTime:    
    def __init__(self, user_id: int):
        self.id = user_id
        self.user_time = Tiempo.query.filter_by(usuario_id=self.id).first()

    def get_time(self):
        return self.user_time.tiempo
              
    def manage_time(self, action, time):
        options = ['add', 'substract']

        if action not in options:
            return "Invalid option"

        if action == 'add':
            self.user_time.tiempo += time
        else:
            self.user_time.tiempo -= time

        db.session.commit()
        return self.user_time.tiempo
