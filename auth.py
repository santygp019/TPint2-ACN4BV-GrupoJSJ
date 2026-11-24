import os
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from db import Session, Usuario, Cliente

auth_bp = Blueprint('auth', __name__)

oauth = OAuth()


def iniciar_google(app):
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def requiere_rol(*roles_permitidos):
    def decorador(f):
        @wraps(f)
        def funcion_envuelta(*args, **kwargs):
            rol_actual = session.get("rol")
            if not rol_actual:
                flash("Tenés que iniciar sesión para acceder a esta sección.")
                return redirect(url_for("auth.login"))
            if rol_actual not in roles_permitidos:
                flash("No tenés permisos suficientes para ver esta sección.")
                return redirect(url_for("home"))
            return f(*args, **kwargs)
        return funcion_envuelta
    return decorador


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        clave = request.form.get("clave", "")

        db_cursor = Session()
        try:
            usuario = db_cursor.query(Usuario).filter_by(email=email, activo=True).first()
        finally:
            db_cursor.close()

        if usuario and usuario.clave_hash and check_password_hash(usuario.clave_hash, clave):
            session.clear()
            session["id_usuario"] = usuario.id_usuario
            session["nombre"] = usuario.nombre
            session["rol"] = usuario.rol
            session["id_cliente"] = usuario.fk_id_cliente
            flash("Bienvenido, " + usuario.nombre + ".")
            return redirect(url_for("home"))

        flash("Email o clave incorrectos.")
        return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefono = request.form.get("telefono", "").strip()
        clave = request.form.get("clave", "")
        confirmar_clave = request.form.get("confirmar_clave", "")

        if not nombre or not email or not clave:
            flash("Completá nombre, email y clave.")
            return redirect(url_for("auth.registro"))

        if len(clave) < 6:
            flash("La clave debe tener al menos 6 caracteres.")
            return redirect(url_for("auth.registro"))

        if clave != confirmar_clave:
            flash("Las claves no coinciden.")
            return redirect(url_for("auth.registro"))

        db_cursor = Session()
        try:
            existente = db_cursor.query(Usuario).filter_by(email=email).first()
            if existente:
                flash("Ya existe una cuenta registrada con ese email.")
                return redirect(url_for("auth.registro"))

            cliente = Cliente(
                nombre=nombre,
                email=email,
                telefono=telefono or None
            )
            db_cursor.add(cliente)
            db_cursor.flush()

            usuario = Usuario(
                nombre=nombre,
                email=email,
                clave_hash=generate_password_hash(clave),
                rol="cliente",
                fk_id_cliente=cliente.id_cliente
            )
            db_cursor.add(usuario)
            db_cursor.commit()

            session.clear()
            session["id_usuario"] = usuario.id_usuario
            session["nombre"] = usuario.nombre
            session["rol"] = usuario.rol
            session["id_cliente"] = usuario.fk_id_cliente

            flash("Cuenta creada con éxito. ¡Bienvenido, " + usuario.nombre + "!")
            return redirect(url_for("home"))
        except Exception as e:
            db_cursor.rollback()
            print("Error en registro:", e)
            flash("No se pudo crear la cuenta. Probá de nuevo.")
            return redirect(url_for("auth.registro"))
        finally:
            db_cursor.close()

    return render_template("registro.html")


@auth_bp.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        info = token.get("userinfo")
    except OAuthError as e:
        print("Error de Google:", e)
        flash("No pudimos iniciar sesión con Google. Probá de nuevo.")
        return redirect(url_for("auth.login"))

    if not info or not info.get("email") or not info.get("email_verified"):
        flash("Google no nos dio un email verificado.")
        return redirect(url_for("auth.login"))

    email = info["email"].strip().lower()
    nombre = info.get("name") or email

    db_cursor = Session()
    try:
        usuario = db_cursor.query(Usuario).filter_by(email=email).first()

        if usuario and not usuario.activo:
            flash("Tu cuenta está desactivada.")
            return redirect(url_for("auth.login"))

        # primera vez que entra con Google: se crea como cliente
        if not usuario:
            cliente = Cliente(nombre=nombre, email=email)
            db_cursor.add(cliente)
            db_cursor.flush()
            usuario = Usuario(
                nombre=nombre,
                email=email,
                clave_hash=None,
                rol="cliente",
                fk_id_cliente=cliente.id_cliente
            )
            db_cursor.add(usuario)
            db_cursor.commit()

        session.clear()
        session["id_usuario"] = usuario.id_usuario
        session["nombre"] = usuario.nombre
        session["rol"] = usuario.rol
        session["id_cliente"] = usuario.fk_id_cliente
    finally:
        db_cursor.close()

    flash("Bienvenido, " + nombre + ".")
    return redirect(url_for("home"))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Cerraste sesión.")
    return redirect(url_for("auth.login"))