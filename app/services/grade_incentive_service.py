from app.models import Incentivos, Restricciones, Settings
from app.utils.filtro_notas_utils import elegir_sistema_calificaciones as grade_system
from app.services.countries_service import get_countries
from app.services.settings_service import UserSettings


def get_currency_data(id, nota):
    incentivos_obj = Incentivos.query.filter_by(usuario_id=id).all()

    incentivos = [{"monto": incentivo.monto, "nota": incentivo.nota} for incentivo in incentivos_obj]

    def evaluar_monto(incentivos, nota):
        for incentivo in incentivos:
            if float(incentivo["nota"]) == float(nota):
                return incentivo["monto"]

    amount = evaluar_monto(incentivos, nota)

    countries = get_countries()
    user_settings = UserSettings(id)
    pais_id = user_settings.get_country()

    for country in countries:
        if country["id"] == pais_id:
            currency = country["moneda"]
            symbol = country["simbolo"]
    
    return amount, currency, symbol

class GradeIncentiveRepository:
    def __init__(self, db_session):
        self.db = db_session

    def add_incentive(self, user_id, message, amount, grade):
        incentive = Incentivos(usuario_id=user_id, condicion=message, monto=amount, nota=grade)
        self.db.add(incentive)

    def add_restriction(self, user_id, message):
        restriction = Restricciones(usuario_id=user_id, restriccion=message)
        self.db.add(restriction)

    def remove_incentive(self, incentive_id):
        incentive = Incentivos.query.filter_by(id=incentive_id).first()
        self.db.delete(incentive)

    def remove_restriction(self, restriction_id):
        restriction = Restricciones.query.filter_by(id=restriction_id).first()
        self.db.delete(restriction)

    def list_incentives(self, user_id):
        incentives_obj = Incentivos.query.filter_by(usuario_id=user_id).all()
        return [{"id": item.id, "incentivo": item.condicion} for item in incentives_obj] 
    
    def list_restrictions(self, user_id):
        restrictions_obj = Restricciones.query.filter_by(usuario_id=user_id).all()
        return [{"id": item.id, "restriccion": item.restriccion} for item in restrictions_obj]

    def get_grades(self, user_id: int) -> list: 
        query = (self.db.query(
            Settings.pais_id,
            Incentivos.nota
        )
        .select_from(Settings)
        .join(Incentivos, Settings.usuario_id == Incentivos.usuario_id)
        .filter(Incentivos.usuario_id == user_id)
        .all()
        )
        
        country = query[0][0]
        result = []
        result.append(country)
    
        for country_id, grade in query:
            grade = str(grade)
            result.append(">=" + grade)
        
        return result
    
    def filter_grades(self, *args) -> list:
        return grade_system(*args)
    
    def commit(self):
        self.db.commit()


class GradeIncentiveMessageFactory:
    @staticmethod
    def create_incentive_message(amount, grade, symbol, currency):
        return f"{symbol}{amount} {currency} for grades >= {grade}"
    
    @staticmethod
    def create_restriction_message(message):
        return message
    

class GradeIncentive:
    def __init__(self, user_id: int, repo: GradeIncentiveRepository):
        self.id = user_id
        self.repo = repo
    
    def add_incentive(self, amount, grade, symbol, currency):
        message = GradeIncentiveMessageFactory.create_incentive_message(amount, grade, symbol, currency)
        self.repo.add_incentive(self.id, message, amount, grade)
        self.repo.commit()
    
    def add_restriction(self, message):
        message = GradeIncentiveMessageFactory.create_restriction_message(message)
        self.repo.add_restriction(self.id, message)
        self.repo.commit()

    def remove_incentive(self, incentive_id):
        self.repo.remove_incentive(incentive_id)
        self.repo.commit()

    def remove_restriction(self, restriction_id):
        self.repo.remove_restriction(restriction_id)
        self.repo.commit()

    def list_information(self):
        return self.repo.list_incentives(self.id), self.repo.list_restrictions(self.id)
    
    def filter_grades(self):
        current_grades = self.repo.get_grades(self.id)
        # print(current_grades)
        return self.repo.filter_grades(*current_grades)
        