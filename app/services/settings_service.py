from app.models import Settings
from .. import db


class UserSettings:
    '''
    Instancia clase con el ID del estudiante, y crea registros iniciales en DB si no los hay.
    '''
    def __init__(self, user_id: int):
        self.id = user_id
        self.user_settings = Settings.query.filter_by(usuario_id=self.id).first()
        self.message = ""
        self.name = self.user_settings.usuario.nombre

        if not self.user_settings:
            self.user_settings = Settings(usuario_id=self.id)
            db.session.add(self.user_settings)
            db.session.commit()
            db.session.refresh(self.user_settings)
            self.message = "User Settings created"
            
    def information(self):
        return self.message
    
    def get_country(self):
        return self.user_settings.pais_id
    
    def incentivo_toggle(self):
        '''
        Alterna estado del incentivo por notas
        '''
        self.user_settings.incentivo_notas = not self.user_settings.incentivo_notas
        db.session.commit()
        return self.user_settings.incentivo_notas
    
    def consultar_incentivo_notas(self):
        '''
        Devuelve estado actual del incentivo por notas
        '''
        return self.user_settings.incentivo_notas

    def consultar_pais(self) -> int:
        return self.user_settings.pais_id
    
    def cambiar_pais(self, pais_id: int):
        self.user_settings.pais_id = pais_id
        db.session.commit()
        return self.user_settings.pais_id

    def get_trophy(self):
        return self.user_settings.trofeo
    
    def set_trophy(self, reward):
        self.user_settings.trofeo = reward
        db.session.commit()
    
    def get_extra_time(self):
        return self.user_settings.extra_time
    
    def set_extra_time(self, extra_time):
        self.user_settings.extra_time = extra_time
        db.session.commit()
    
    def get_study_fun_ratio(self):
        return self.user_settings.time_ratio
    
    def set_study_fun_ratio(self, time_ratio):
        self.user_settings.time_ratio = time_ratio
        db.session.commit()