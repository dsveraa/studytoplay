from flask import flash, render_template, request, redirect, url_for, session, Blueprint

from app.repositories.user_repository import UserRepository
from app.services.login_service import LoginService
from app.services.signup_service import SignUpService
from app.services.user_service import UserService
from app.utils.debugging_utils import printn


auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login")
def login_view():
    email = request.args.get('email', '')
    return render_template("login.html", email=email)

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form["correo"]
    password = request.form["contrasena"]
    
    try:
        LoginService.login(email, password)
        return redirect(url_for("core.home"))
    
    except ValueError as e:
        flash(str(e), "error")
        return render_template("login.html", email=email)


@auth_bp.route("/registro")
def registro_view():
    roles = UserService.get_all_roles()
    default_role = UserRepository.get_role_obj_by_name('student')
    selected_role = request.args.get("rol_seleccionado", default_role.id if default_role else None)
    return render_template("registro.html", roles=roles, rol_seleccionado=selected_role)


@auth_bp.route("/registro", methods=["POST"])
def registro():
    name = request.form["nombre"]
    email = request.form["email"]
    password = request.form["contrasena"]
    repeat_password = request.form["repetir_contrasena"]
    role = request.form["role"]
    
    try:
        SignUpService.signup(name, email, password, repeat_password, role)
        return redirect(url_for("auth.login_view"))
    
    except ValueError as e:
        errors = e.args[0]
        if isinstance(errors, list):
            for msg in errors:
                flash(msg, "warning")
        else:
            flash(str(e), "warning")

        roles = UserService.get_all_roles()
        return render_template("registro.html", roles=roles, nombre=name, rol_seleccionado=role, email=email)
    

@auth_bp.route("/logout")
def logout():
    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)
    session.pop("supervisor_id", None)
    return redirect(url_for("core.home"))
