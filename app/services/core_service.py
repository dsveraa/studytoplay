from app.utils.helpers import check_new_notifications, set_level, set_stars, set_trophies


class CoreService:
    @staticmethod
    def check_and_set_up(user_id):
        check_new_notifications(user_id)
        set_level(user_id)
        set_stars(user_id)
        set_trophies(user_id)