import pytest
import os
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.relaciones_model import SupervisorEstudiante
from app.models.users_model import Usuario, Rol
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def app():
    os.environ['ENVIRONMENT'] = 'testing'
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        db.session.execute(text("TRUNCATE TABLE usuarios RESTART IDENTITY CASCADE"))
        db.session.execute(text("TRUNCATE TABLE roles RESTART IDENTITY CASCADE"))
        db.session.commit()
        yield app

@pytest.fixture
def usuario(app):
    rol = db.session.query(Rol).first()
    if not rol:
        rol = Rol(nombre="TestRole")
        db.session.add(rol)
        db.session.commit()

    user = Usuario(
        nombre="Usuario Test",
        correo="test@example.com",
        contrasena=generate_password_hash("password123"),
        rol_id=rol.id
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def db_session():
    """Crea una sesión de base de datos aislada para cada test (compatible con Flask-SQLAlchemy 3.x)."""
    connection = db.engine.connect()
    transaction = connection.begin()

    # Crea una sesión aislada sin reemplazar db.session
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session  # se entrega al test

    # Limpieza
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def supervisor_and_student():
    # Crear roles
    rol_supervisor = Rol(nombre="supervisor")
    rol_estudiante = Rol(nombre="student")
    db.session.add_all([rol_supervisor, rol_estudiante])
    db.session.commit()

    # Crear usuarios
    supervisor = Usuario(
        nombre="Supervisor",
        correo="sup@example.com",
        contrasena="hash",
        rol_id=rol_supervisor.id
    )
    estudiante = Usuario(
        nombre="Estudiante",
        correo="est@example.com",
        contrasena="hash",
        rol_id=rol_estudiante.id
    )
    db.session.add_all([supervisor, estudiante])
    db.session.commit()

    # Crear relación supervisor-estudiante
    relacion = SupervisorEstudiante(
        supervisor_id=supervisor.id,
        estudiante_id=estudiante.id
    )
    db.session.add(relacion)
    db.session.commit()

    return supervisor, estudiante