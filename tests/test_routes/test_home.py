import pytest
from flask import session
from app.models.users_model import Usuario, Rol
from app import db

@pytest.fixture
def supervisor_user(app):
    """Crea un usuario con rol supervisor"""
    rol = db.session.query(Rol).filter_by(nombre="supervisor").first()
    if not rol:
        rol = Rol(nombre="supervisor")
        db.session.add(rol)
        db.session.commit()

    user = Usuario(
        nombre="Supervisor Test",
        correo="supervisor@example.com",
        contrasena="hashed_pw",
        rol_id=rol.id
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_home_redirects_if_not_logged_in(client):
    """Si no hay usuario en sesión, debe redirigir al login"""
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location


def test_home_redirects_if_not_supervisor(client, usuario):
    """Si usuario está logueado pero no es supervisor, redirige a perfil"""
    with client.session_transaction() as sess:
        sess["usuario_id"] = usuario.id

    response = client.get("/")
    assert response.status_code == 302
    assert "/perfil" in response.location


def test_home_renders_dashboard_for_supervisor(client, supervisor_user):
    """Si usuario es supervisor, renderiza dashboard"""
    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor_user.id

    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data
