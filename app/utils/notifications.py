from datetime import timedelta
from app.models import Usuario, NuevaNotificacion, Notificaciones

from .. import db
from functools import wraps
from flask import session, jsonify, url_for
from sqlalchemy.orm import aliased
from sqlalchemy import desc
from app.utils.debugging import printn

class Notification:
    def __init__(self, id):
        self.id = id
        
    def notify_grade(self, grade, subject, action):
        if action == 'add':
            message = f'You will be rewarded for a grade of {grade} in {subject}!'
        elif action == 'pay':
            message = f'You have been rewarded for a grade of {grade} in {subject}!'
        else:
            raise ValueError("Invalid action. Expected 'add' or 'pay'.")
                
        notification = Notificaciones(usuario_id=self.id, notificacion=message, leida=False)
        db.session.add(notification)
        
        new_notification = NuevaNotificacion.query.filter_by(usuario_id=self.id).first()
        new_notification.estado = True
        db.session.commit()