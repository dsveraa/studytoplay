from app.models.gamification_model import Incentivos, Restricciones


class GamificacionRepository:
    @staticmethod
    def get_incentives_obj_by_user_id(user_id):
        return Incentivos.query.filter_by(usuario_id=user_id).all()
    
    @staticmethod
    def get_restrictions_obj_by_user_id(user_id):
        return Restricciones.query.filter_by(usuario_id=user_id).all()
    

    @staticmethod
    def get_last_incentive_by_user_id(user_id):
        return Incentivos.query.filter_by(usuario_id=user_id).order_by(Incentivos.id.desc()).first()
