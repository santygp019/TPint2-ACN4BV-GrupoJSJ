from flask import request, render_template
from db import Session, Compra, DetalleCompra, Producto, Proveedor


def cargar_formulario_compra(mensaje=""):
    db_cursor = Session()
    try:
        proveedores = db_cursor.query(Proveedor).all()
        productos = db_cursor.query(Producto).filter_by(activo=True).all()
        return render_template(
            "agregar_compra.html",
            proveedores=proveedores,
            productos=productos,
            mensaje=mensaje
        )
    finally:
        db_cursor.close()


def procesar_nueva_compra():
    db_cursor = Session()
    try:
        try:
            id_prov = int(request.form["id_proveedor"])
            id_prod = int(request.form["id_producto"])
            cant = int(request.form["cantidad"])
            precio = float(request.form["precio_compra"])
        except (KeyError, ValueError, TypeError):
            return cargar_formulario_compra(mensaje="Error: Completá todos los campos con valores válidos.")

        if cant < 1:
            return cargar_formulario_compra(mensaje="Error: La cantidad debe ser mayor o igual a 1.")

        if precio < 1:
            return cargar_formulario_compra(mensaje="Error: El precio de compra debe ser mayor o igual a 1.")

        proveedor = db_cursor.query(Proveedor).filter_by(id_proveedor=id_prov).first()
        if not proveedor:
            return cargar_formulario_compra(mensaje="Error: El proveedor seleccionado no existe.")

        producto = db_cursor.query(Producto).filter_by(id_producto=id_prod, activo=True).first()
        if not producto:
            return cargar_formulario_compra(mensaje="Error: El producto seleccionado no existe o está eliminado.")

        nueva_compra = Compra(fk_id_proveedor=id_prov)
        db_cursor.add(nueva_compra)
        db_cursor.flush()

        nuevo_detalle = DetalleCompra(
            fk_id_compra=nueva_compra.id_compra,
            fk_id_producto=id_prod,
            cantidad=cant,
            precio_compra=precio
        )
        db_cursor.add(nuevo_detalle)

        producto.stock += cant

        db_cursor.commit()
        return cargar_formulario_compra(mensaje="¡Compra registrada y stock actualizado con éxito!")

    except Exception as e:
        db_cursor.rollback()
        return cargar_formulario_compra(mensaje=f"Error al registrar: {str(e)}")

    finally:
        db_cursor.close()


def historial_compras():
    db_cursor = Session()
    try:
        id_proveedor = request.args.get("id_proveedor")
        fecha_buscada = request.args.get("fecha")

        query = db_cursor.query(Compra).join(Proveedor)

        if id_proveedor and id_proveedor != "todos":
            query = query.filter(Compra.fk_id_proveedor == id_proveedor)

        if fecha_buscada:
            query = query.filter(Compra.fecha.like(f"{fecha_buscada}%"))

        compras = query.order_by(Compra.fecha.desc()).all()
        proveedores = db_cursor.query(Proveedor).all()

        return render_template("historial_compras.html", compras=compras, proveedores=proveedores)
    finally:
        db_cursor.close()