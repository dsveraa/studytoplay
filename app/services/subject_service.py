from app.models.academic_model import Asignatura
from app.repositories.record_repository import RecordRepository
from app.repositories.subject_repository import SubjectRepository
from app.services.record_service import RecordService


class SubjectService:
    @staticmethod
    def add_subject(user_id, subject):
        new_subject = SubjectRepository.add_subject(user_id, subject)
        SubjectRepository.add(new_subject)
        SubjectRepository.commit()
        return new_subject
    
    @staticmethod
    def edit_subject(user_id, subject_id, new_name):
        subject = SubjectRepository.get_one_subject_by_id_and_user_id(subject_id, user_id)
        
        if not subject:
            raise ValueError('User Id or Subject Id not found')

        subject.nombre = new_name
        SubjectRepository.commit()
        return new_name
        
    @staticmethod
    def delete_subject(user_id, subject_id):
        subject = SubjectRepository.get_one_subject_by_id_and_user_id(subject_id, user_id)
        
        if not subject:
            raise ValueError('User Id or Subject Id not found')

        SubjectRepository.delete(subject)
        SubjectRepository.commit()

    @staticmethod
    def transform_obj_subject_to_list(obj):
        return [{
        'id': sub.id,
        'name': sub.nombre,
        'user_id': sub.usuario_id
    }
    for sub in obj]

    @staticmethod
    def get_subject_obj_by_user_id(user_id):
        return SubjectRepository.get_all_subjects_by_user_id(user_id)
        
    @staticmethod
    def get_subject_name(activity_id):
        if activity_id:
            subject_obj = SubjectRepository.get_subject_by_id(activity_id)
            subject_name = subject_obj.nombre if subject_obj else "Unknown"
        else:
            subject_name = "Latest"
        return subject_name
        
    @staticmethod
    def get_subjects_dict(user_id):
        subject_obj = SubjectService.get_subject_obj_by_user_id(user_id)    
        return {subject.id: subject.nombre for subject in subject_obj}

    @staticmethod
    def get_subject_percentage(time_by_subject, user_id):
        individual_time_by_subject = RecordService.get_individual_time(time_by_subject)
        subjects_dict = SubjectService.get_subjects_dict(user_id)
        total = sum(individual_time_by_subject.values())
        return { name: str(round((individual_time_by_subject.get(asig_id, 0) / total * 100), 1)) if total > 0 else "0.0" for asig_id, name in subjects_dict.items()}