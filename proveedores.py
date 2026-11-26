from flask import request, render_template, redirect, url_for
from sqlalchemy import func
from db import Session, Proveedor


def agregarProveedor():
    db_cursor = Session()
    error = None

    try:
        if request.method == "POST":
            nombre_proveedor = request.form.get("nombre", "").strip()

            if not nombre_proveedor:
                error = "El nombre del proveedor es obligatorio."
            else:
                existente = (
                    db_cursor.query(Proveedor)
                    .filter(func.lower(Proveedor.nombre) == nombre_proveedor.lower())
                    .first()
                )
                if existente:
                    error = f"Ya existe un proveedor registrado con el nombre '{nombre_proveedor}'."
                else:
                    nuevo_proveedor = Proveedor(nombre=nombre_proveedor)
                    db_cursor.add(nuevo_proveedor)
                    db_cursor.commit()
                    return redirect(url_for("cargarProveedor"))

        proveedores = db_cursor.query(Proveedor).all()
        return render_template("agregar_proveedor.html", proveedores=proveedores, error=error)
    finally:
        db_cursor.close()