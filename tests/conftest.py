import pytest
import os
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.users_model import Usuario, Rol

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

