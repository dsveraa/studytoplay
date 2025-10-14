from sqlalchemy.orm import aliased
from app import db
from app.models.gamification_model import Incentivos
from app.models.relations_model import SupervisorEstudiante
from app.models.time_model import Tiempo
from app.models.users_model import EstadoUsuario, Settings, Usuario


class HomeRepository:
    @staticmethod
    def get_students(user_id):
        Estudiante = aliased(Usuario)
        Supervisor = aliased(Usuario)

        return (
            db.session.query(
                Estudiante.id,
                Estudiante.nombre,
                Tiempo.tiempo,
                EstadoUsuario.estado,
                Settings.incentivo_notas,
                Incentivos.id
            )
            .select_from(SupervisorEstudiante)
            .join(Supervisor, Supervisor.id == SupervisorEstudiante.supervisor_id)
            .join(Estudiante, Estudiante.id == SupervisorEstudiante.estudiante_id)
            .outerjoin(Tiempo, Tiempo.usuario_id == SupervisorEstudiante.estudiante_id)
            .outerjoin(EstadoUsuario, EstadoUsuario.usuario_id == SupervisorEstudiante.estudiante_id)
            .outerjoin(Settings, Settings.usuario_id == Estudiante.id)
            .outerjoin(Incentivos, Incentivos.usuario_id == Estudiante.id)
            .filter(SupervisorEstudiante.supervisor_id == user_id)
            .distinct(Estudiante.id)
        )
    