from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from db import Session, Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        clave = request.form.get("clave", "")

        # buscar al usuario por su email
        db_cursor = Session()
        try:
            usuario = db_cursor.query(Usuario).filter_by(email=email, activo=True).first()
        finally:
            db_cursor.close()

        # comparar la clave escrita con el hash guardado
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


@auth_bp.route('/logout')
def logout():
    # borrar todo lo guardado en la sesión
    session.clear()
    flash("Cerraste sesión.")
    return redirect(url_for("auth.login"))