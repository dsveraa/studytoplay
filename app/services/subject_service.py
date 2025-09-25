from app.repositories.subject_repository import SubjectRepository


class SubjectService:
    @staticmethod
    def add_subject(user_id, subject):
        new_subject = SubjectRepository.add_subject(user_id, subject)
        SubjectRepository.add(new_subject)
        SubjectRepository.commit()
        return new_subject
    
    @staticmethod
    def edit_subject(user_id, subject_id, new_name):
        subject = SubjectRepository.get_subject_by_id_and_user_id(subject_id, user_id)
        
        if not subject:
            raise ValueError('User Id or Subject Id not found')

        subject.nombre = new_name
        SubjectRepository.commit()
        return new_name
        
    @staticmethod
    def delete_subject(user_id, subject_id):
        subject = SubjectRepository.get_subject_by_id_and_user_id(subject_id, user_id)
        
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
    
