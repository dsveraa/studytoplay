import pytest
from app.models import Usuario
from app import db


@pytest.fixture
def usuario_test():
    user = Usuario(
        nombre="visitor",
        correo="visitor@mail.com",
        contrasena="test123",
        rol_id=1
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()


def test_lista_usuarios(client, usuario_test):
    response = client.get("/usuarios")
    assert response.status_code == 200
    assert b"visitor" in response.data
