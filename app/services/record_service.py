from app.repositories.record_repository import RecordRepository


class RecordService:
    @staticmethod
    def edit_record(id, user_id, new_summary=''):
        record = RecordRepository(id, user_id)
        record.set_summary(new_summary)
        record.commit()
        return record.resumen
    
    @staticmethod
    def get_activity_obj(user_id, activity_id):
        if activity_id:
            activity_obj = RecordRepository.get_list_by_activity(user_id, activity_id)
        else:
            limit = 20
            activity_obj = RecordRepository.get_full_list(user_id, limit)
        return activity_obj
    
    @staticmethod
    def get_time_by_subject(user_id):
        return RecordRepository.get_time_by_subject(user_id)
    
    @staticmethod
    def get_individual_time(time_by_subject):
        return {subject_id: time for subject_id, time in time_by_subject}
    
    @staticmethod
    def add_study_session(user_id, start_date, end_date, summary, subject_id):
        new_study = RecordRepository.set_study_obj(user_id, start_date, end_date, summary, subject_id)
        RecordRepository.add(new_study)
        print("todo bien por aquí <-----")
