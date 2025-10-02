from app.repositories.record_repository import RecordRepository


class RecordService:
    @staticmethod
    def edit_record(id, user_id, new_summary=''):
        record = RecordRepository(id, user_id)
        record.set_summary(new_summary)
        record.commit()
        return record.resumen
    