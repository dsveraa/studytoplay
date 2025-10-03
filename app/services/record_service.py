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
    