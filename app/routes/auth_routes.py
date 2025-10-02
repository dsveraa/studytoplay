from flask import flash, render_template, request, redirect, url_for, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import Usuario, Rol, NuevaNotificacion
from app.services.user_service import UserService
from app.utils.debugging_utils import printn

from .. import db


auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login")
def login_view():
    email = request.args.get('email', '')
    return render_template("login.html", email=email)

@auth_bp.route("/login", methods=["POST"])
def login():
    correo = request.form["correo"]
    contrasena = request.form["contrasena"]
    
    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario:
        flash("User doesn't exist.", "error")
        return render_template("login.html", email=correo)
    
    if not check_password_hash(usuario.contrasena, contrasena):
        flash("Incorrect password.", "error")
        return render_template("login.html", email=correo)

    session["usuario_id"] = usuario.id
    session["usuario_nombre"] = usuario.nombre

    supervisor = Usuario.query.join(Rol).filter(
        Usuario.id == usuario.id,
        Rol.nombre == "supervisor"
    ).first()
    
    if supervisor:
        session["supervisor_id"] = usuario.id

    session.permanent = True

    return redirect(url_for("core.home"))
    

@auth_bp.route("/registro")
def registro_view():
    roles = UserService.get_all_roles()
    
    rol_default = Rol.query.filter_by(nombre='estudiante').first()
    print(rol_default)
    rol_seleccionado = request.args.get("rol_seleccionado", rol_default.id if rol_default else None)
    print(rol_seleccionado)
    return render_template("registro.html", roles=roles, rol_seleccionado=rol_seleccionado)


@auth_bp.route("/registro", methods=["POST"])
def registro():
    nombre = request.form["nombre"]
    email = request.form["email"]
    contrasena = request.form["contrasena"]
    repetir_contrasena = request.form["repetir_contrasena"]
    rol = request.form["role"]
    
    email_exists = True if Usuario.query.filter_by(correo=email).first() else False
    wrong_password = True if contrasena != repetir_contrasena else False

    if email_exists:
        flash(f"E-mail <b>{email}</b> is already used.", 'warning')
    
    if wrong_password:
        flash("Passwords doesn't match, try again.", 'warning')
    
    if email_exists or wrong_password:
        roles = UserService.get_all_roles()
        return render_template("registro.html", roles=roles, nombre=nombre, rol_seleccionado=rol, email=email)
    
    if rol == "1":
        rol_obj = Rol.query.filter_by(nombre='student').first()
    else:
        rol_obj = Rol.query.filter_by(nombre='supervisor').first()

    contrasena_hash = generate_password_hash(contrasena)
    
    nuevo_usuario = Usuario(nombre=nombre, correo=email, contrasena=contrasena_hash, rol=rol_obj)
    db.session.add(nuevo_usuario)
    db.session.commit()

    user_id = UserService.get_id_from_email(email)
    default = NuevaNotificacion(usuario_id=user_id, estado=False)
    db.session.add(default)
    db.session.commit()

    return redirect(url_for("auth.login_view"))
    

@auth_bp.route("/usuarios")
def mostrar_usuarios():
    usuarios = Usuario.query.all()
    return '<br>'.join([f'{usuario.nombre} ({usuario.correo})' for usuario in usuarios])


@auth_bp.route("/logout")
def logout():
    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)
    session.pop("supervisor_id", None)
    return redirect(url_for("core.home"))

