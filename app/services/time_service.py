from app.repositories.time_repository import TimeRepository
from app.services.settings_service import UserSettings
from .. import db


class UserTime:    
    def __init__(self, user_id: int):
        self.id = user_id
        self.time_obj = TimeRepository.get_time_object(user_id)

    def get_time(self):
        if not self.time_obj:
            query = TimeRepository.time_init(self.id)
            TimeRepository.add(query)
            TimeRepository.commit()
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
    
    def record_time(self, time):
        self.time_obj.tiempo = time
        
    @staticmethod
    def handle_new_time(user_id, new_time):
        time_obj = TimeRepository.get_time_obj_by_user_id(user_id)
        time_accumulation = TimeRepository.get_time_accumulation_by_user_id(user_id)
        
        user_settings = UserSettings(user_id)
        multiplier = user_settings.get_study_fun_ratio()
        
        if time_obj:
            time_obj.tiempo += (new_time * multiplier)
        else:
            TimeRepository.create_time(user_id, new_time)
            
        if time_accumulation:
            time_accumulation.cantidad += new_time
        else:
            TimeRepository.create_acc_time(user_id, new_time)

        db.session.commit()
        db.session.refresh(time_accumulation)
    
    @staticmethod
    def add_use(user_id, start_date, end_date, activity, remaining_time):
        new_use = TimeRepository.set_new_use(user_id, start_date, end_date, activity, remaining_time)
        TimeRepository.add(new_use)
        TimeRepository.commit()
 