from .notifications_routes import notificaciones_bp
from .core_routes import core_bp
from .relationship_routes import relaciones_bp
from .gamification_routes import gamificacion_bp
from .auth_routes import auth_bp
from .super_routes import super_bp
from .time_routes import tiempo_bp
from .academic_routes import academico_bp


def register_routes(app):
    app.register_blueprint(notificaciones_bp, url_prefix='')
    app.register_blueprint(core_bp, url_prefix='')
    app.register_blueprint(relaciones_bp, url_prefix='')
    app.register_blueprint(gamificacion_bp, url_prefix='')
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(super_bp, url_prefix='')
    app.register_blueprint(tiempo_bp, url_prefix='')
    app.register_blueprint(academico_bp, url_prefix='')
