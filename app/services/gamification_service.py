from typing import List

from app.repositories.gamification_repository import GamificacionRepository
from app.utils.helpers import make_stars_template, show_stars


class GamificacionService:
    @staticmethod
    def get_stars(user_id) -> List[int]:
        stars_amount: int = show_stars(user_id)
        return  make_stars_template(stars_amount)
    
    @staticmethod
    def get_incentives(user_id):
        incentives_obj = GamificacionRepository.get_incentives_obj_by_user_id(user_id)
        return [incentive.condicion for incentive in incentives_obj]

    @staticmethod
    def get_restrictions(user_id):
        restrictions_obj = GamificacionRepository.get_restrictions_obj_by_user_id(user_id)
        return [restriction.restriccion for restriction in restrictions_obj]
    
    @staticmethod
    def get_last_incentive(user_id):
        return GamificacionRepository.get_last_incentive_by_user_id(user_id)
