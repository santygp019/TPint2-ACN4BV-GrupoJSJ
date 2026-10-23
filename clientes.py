from flask import request, render_template, redirect, url_for
from db import Session, Cliente


## Valida los datos del formulario, devuelve un mensaje de error o None si esta todo bien
def validarCliente(nombre, email, telefono):
    if not nombre:
        return "El nombre es obligatorio."

    if not email and not telefono:
        return "Ingresá al menos un dato de contacto (email o teléfono)."

    if email and ("@" not in email or "." not in email.split("@")[-1]):
        return "El email no tiene un formato válido."

    solo_numeros = telefono.replace(" ", "").replace("-", "").replace("+", "")
    if telefono and (not solo_numeros.isdigit() or not 6 <= len(solo_numeros) <= 15):
        return "El teléfono no tiene un formato válido."

    return None


def agregarCliente():
    db_cursor = Session()
    error = None

    ## capturamos nuestro formulario
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip()
        telefono = request.form["telefono"].strip()

        error = validarCliente(nombre, email, telefono)

        if not error:
            nuevo_cliente = Cliente(nombre=nombre, email=email, telefono=telefono)
            db_cursor.add(nuevo_cliente)
            db_cursor.commit()
            db_cursor.close()

            return redirect(url_for("cargarCliente"))

    ## solo mostramos los clientes que no fueron dados de baja
    clientes = db_cursor.query(Cliente).filter_by(activo=True).all()
    db_cursor.close()

    return render_template("clientes.html", clientes=clientes, error=error)


def editarCliente(id_cliente):
    db_cursor = Session()
    cliente = db_cursor.query(Cliente).filter_by(id_cliente=id_cliente, activo=True).first()

    if not cliente:
        db_cursor.close()
        return redirect(url_for("cargarCliente"))

    error = None

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        email = request.form["email"].strip()
        telefono = request.form["telefono"].strip()

        error = validarCliente(nombre, email, telefono)

        if not error:
            cliente.nombre = nombre
            cliente.email = email
            cliente.telefono = telefono
            db_cursor.commit()
            db_cursor.close()

            return redirect(url_for("cargarCliente"))

    pagina = render_template("editar_cliente.html", cliente=cliente, error=error)
    db_cursor.close()

    return pagina


## Baja logica: no borramos la fila para no perder el historial de compras del cliente
def darBajaCliente(id_cliente):
    db_cursor = Session()

    cliente = db_cursor.query(Cliente).filter_by(id_cliente=id_cliente).first()

    if cliente:
        cliente.activo = False
        db_cursor.commit()

    db_cursor.close()

    return redirect(url_for("cargarCliente"))
