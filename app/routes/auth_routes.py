from flask import render_template, request, redirect, url_for, session, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import Usuario, Rol, NuevaNotificacion

from .. import db


auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]
        
        usuario = Usuario.query.filter_by(correo=correo).first()
        
        if usuario and check_password_hash(usuario.contrasena, contrasena):
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            
            usuario_id = session.get('usuario_id')
            supervisor = Usuario.query.join(Rol).filter(Usuario.id == usuario_id, Rol.nombre == "supervisor").first()
            
            if supervisor:
                session["supervisor_id"] = usuario_id

            session.permanent = True

            nueva_notificacion = NuevaNotificacion.query.filter_by(usuario_id=usuario_id).first()

            if not nueva_notificacion:
                entrada_default = NuevaNotificacion(usuario_id=usuario_id, estado=False)
                db.session.add(entrada_default)
                db.session.commit()
            
            if "supervisor_id" in session:
                print("supervisor_id existe en session")
            else:
                print("No existe supervisor_id en session")

            return redirect(url_for("core.home"))
        else:
            return "Correo o contraseña incorrectos."

    return render_template("login.html")

@auth_bp.route("/registro", methods=["GET","POST"])
def registro():
    role_obj = Rol.query.all()
    roles = [{'id': role.id, 'rol': role.rol} for role in role_obj]
    # print(roles)

    if request.method == 'POST':
        nombre = request.form["nombre"]
        email = request.form["email"]
        contrasena = request.form["contrasena"]
        repetir_contrasena = request.form["repetir_contrasena"]
        rol = request.form["role"]
        
        if contrasena != repetir_contrasena:
            return "Las contraseñas no coinciden, intenta nuevamente."
        
        if Usuario.query.filter_by(correo=email).first():
            return "El correo ya está registrado, intenta con otro."
        
        contrasena_hash = generate_password_hash(contrasena)
        
        nuevo_usuario = Usuario(nombre=nombre, correo=email, contrasena=contrasena_hash, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return redirect(url_for("auth.login"))
    return render_template("registro.html", roles=roles, rol_seleccionado='student')

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

