from .. import db
from app.models import Asignatura

class SubjectRepository:
    @staticmethod
    def get_all_subjects_by_user_id(user_id):
        return Asignatura.query.filter_by(usuario_id=user_id).all()
    
    @staticmethod
    def get_subject_by_id(subject_id):
        return Asignatura.query.filter_by(id=subject_id).first()
    
    @staticmethod
    def get_subject_by_id_and_user_id(subject_id, user_id):
        return Asignatura.query.filter_by(id=subject_id, usuario_id=user_id).first()
    
    @staticmethod
    def add_subject(user_id, subject):
        return Asignatura(nombre=subject, usuario_id=user_id)

    @staticmethod
    def add(object):
        return db.session.add(object)

    @staticmethod
    def delete(object):
        return db.session.delete(object)
            
    @staticmethod
    def commit():
        db.session.commit()

