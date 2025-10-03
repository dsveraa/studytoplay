from app.repositories.home_repository import HomeRepository


class HomeService:
    @staticmethod
    def get_students(user_id):
        query = HomeRepository.get_students(user_id)

        return [
            {   
                "id": eid, 
                "nombre": nombre, 
                "tiempo": tiempo, 
                "estado": estado, 
                "grade_incentive": incentivo_notas,
                "incentivo_id": inc_id
            }
            for eid, nombre, tiempo, estado, incentivo_notas, inc_id in query.all()
        ]