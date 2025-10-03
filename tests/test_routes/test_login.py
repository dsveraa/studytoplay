import pytest
from flask import session
from werkzeug.security import generate_password_hash
from app import db
from app.models import Usuario, Rol


@pytest.fixture
def usuario_normal(app):
    rol = Rol(nombre="estudiante")
    db.session.add(rol)
    db.session.commit()

    usuario = Usuario(
        nombre="Usuario Normal",
        correo="normal@example.com",
        contrasena=generate_password_hash("password123"),
        rol_id=rol.id,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


@pytest.fixture
def usuario_supervisor(app):
    rol = Rol(nombre="supervisor")
    db.session.add(rol)
    db.session.commit()

    usuario = Usuario(
        nombre="Supervisor",
        correo="supervisor@example.com",
        contrasena=generate_password_hash("password123"),
        rol_id=rol.id,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def test_login_view_get(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"login" in resp.data.lower()

    resp = client.get("/login?email=test@example.com")
    assert b"value=\"test@example.com\"" in resp.data


def test_login_user_does_not_exist(client):
    resp = client.post("/login", data={"correo": "nouser@example.com", "contrasena": "123"})
    assert resp.status_code == 200       
    assert b"User doesn't exist." in resp.data


def test_login_incorrect_password(client, usuario_normal):
    resp = client.post("/login", data={"correo": usuario_normal.correo, "contrasena": "wrongpass"})
    assert resp.status_code == 200
    assert b"Incorrect password." in resp.data


def test_login_success(client, usuario_normal):
    with client:
        resp = client.post("/login", data={"correo": usuario_normal.correo, "contrasena": "password123"})
        assert resp.status_code == 302
        assert "/" in resp.location
        assert session["usuario_id"] == usuario_normal.id
        assert session["usuario_nombre"] == usuario_normal.nombre
        assert "supervisor_id" not in session


def test_login_supervisor(client, usuario_supervisor):
    with client:
        resp = client.post("/login", data={"correo": usuario_supervisor.correo, "contrasena": "password123"})
        assert resp.status_code == 302
        assert "/" in resp.location
        assert session["usuario_id"] == usuario_supervisor.id
        assert session["supervisor_id"] == usuario_supervisor.id
