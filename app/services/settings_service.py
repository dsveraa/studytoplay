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

        if not self.user_settings:
            self.user_settings = Settings(usuario_id=self.id)
            db.session.add(self.user_settings)
            db.session.commit()
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

    def consultar_pais(self):
        return self.user_settings.pais_id
    
    def cambiar_pais(self, pais_id: int):
        self.user_settings.pais_id = pais_id
        db.session.commit()
        return self.user_settings.pais_id
