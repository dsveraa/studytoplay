from app.models import Settings
from .. import db

class UserSettings:
    def __init__(self, user_id):
        self.id = user_id
        self.user_settings = Settings.query.filter_by(usuario_id=self.id).first()

        if not self.user_settings:
            self.user_settings = Settings(usuario_id=self.id)
            db.session.add(self.user_settings)
            db.session.commit()
    
    def incentivo_toggle(self):
        self.user_settings.incentivo_notas = not self.user_settings.incentivo_notas
        db.session.commit()
        return self.user_settings.incentivo_notas

    def pais(self):
        print("pass")

