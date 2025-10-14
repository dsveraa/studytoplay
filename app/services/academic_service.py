from app.repositories.academic_repository import AcademicRepository


class AcademicService:
    @staticmethod
    def add_grade(user_id, subject_id, topic, grade, date):
        obj = AcademicRepository.set_grade(user_id, subject_id, topic, grade, date)
        AcademicRepository.add_grade(obj)
        AcademicRepository.commit()

    @staticmethod
    def get_grade_and_subject(record_id):
        grade_obj = AcademicRepository.get_grade_by_id(record_id)
        grade = grade_obj.nota
        subject = grade_obj.asignatura.nombre
        grade_obj.estado = True

        return grade, subject   
    
    @staticmethod
    def set_grade_as_paid(record_id):
        AcademicRepository.set_grade_as_payed(record_id)
        AcademicRepository.commit()
        