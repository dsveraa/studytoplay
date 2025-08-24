from app.models import Incentivos, Restricciones

class IncentiveRestrictionRepository:
    def __init__(self, db_session):
        self.db = db_session

    def add_incentive(self, usuario_id, mensaje, monto, nota):
        incentivo = Incentivos(
            usuario_id=usuario_id, condicion=mensaje, monto=monto, nota=nota
        )
        self.db.add(incentivo)

    def add_restriction(self, usuario_id, mensaje):
        restriccion = Restricciones(
            usuario_id=usuario_id, restriccion=mensaje
        )
        self.db.add(restriccion)

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
    
    def commit(self):
        self.db.commit()


class IncentivesMessageFactory:
    @staticmethod
    def create_incentive_message(monto, nota, simbolo, moneda):
        return f"{simbolo}{monto} {moneda} for grades >= {nota}"
    
    @staticmethod
    def create_restriction_message(message):
        return message
    

class IncentiveManagement:
    def __init__(self, user_id: int, repo: IncentiveRestrictionRepository):
        self.id = user_id
        self.repo = repo
    
    def add_incentive(self, monto, nota, simbolo, moneda):
        message = IncentivesMessageFactory.create_incentive_message(monto, nota, simbolo, moneda)
        self.repo.add_incentive(self.id, message, monto, nota)
        self.repo.commit()
    
    def add_restriction(self, mensaje):
        message = IncentivesMessageFactory.create_restriction_message(mensaje)
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
    