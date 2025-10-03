import pytest
from werkzeug.security import generate_password_hash
from app.models import Usuario, Rol
from app import db

@pytest.fixture
def usuario_test(app):
    rol = db.session.query(Rol).first()
    if not rol:
        rol = Rol(nombre="TestRole")
        db.session.add(rol)
        db.session.commit()

    user = Usuario(
        nombre="visitor",
        correo="visitor@mail.com",
        contrasena=generate_password_hash("test123"),
        rol_id=rol.id
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()
