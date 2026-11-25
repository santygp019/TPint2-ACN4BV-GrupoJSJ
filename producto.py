from flask import Flask, request, render_template, redirect, url_for
from db import Session, Producto, Categoria


## Valida los datos del formulario, devuelve un mensaje de error o None si esta todo bien
def validarProducto(nombre, precio, stock):
    if not nombre:
        return "El nombre es obligatorio."

    if precio == "" or stock == "":
        return "El precio y el stock no pueden estar vacíos."

    try:
        precio_num = float(precio)
        stock_num = int(stock)
    except ValueError:
        return "El precio debe ser un número y el stock un número entero."

    if precio_num <= 0:
        return "El precio debe ser mayor a 0."

    if stock_num < 0:
        return "El stock no puede ser negativo."

    return None


def agregarProductos():
    db_cursor = Session()
    error = None

    try:
        ## capturamos nuestro formulario
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            precio = request.form.get("precio", "").strip()
            stock = request.form.get("stock", "").strip()
            id_categoria = request.form.get("id_categoria", "").strip()

            error = validarProducto(nombre, precio, stock)

            if not error:
                try:
                    nuevo_producto = Producto(
                        nombre=nombre,
                        precio=float(precio),
                        stock=int(stock),
                        fk_id_categoria=int(id_categoria)
                    )
                    ## Lo agregamos y hacemos commit
                    db_cursor.add(nuevo_producto)
                    db_cursor.commit()
                    return redirect(url_for("cargarProducto"))
                except ValueError:
                    error = "Datos inválidos en el formulario."

        productos = db_cursor.query(Producto).filter_by(activo=True).all()
        categorias = db_cursor.query(Categoria).all() ## Esto es igual a hacer un select * from categoria
        return render_template("agregar_productos.html", productos=productos, categorias=categorias, error=error)
    finally:
        db_cursor.close()


def editarProducto(id_producto):
    db_cursor = Session()
    try:
        producto = db_cursor.query(Producto).filter_by(id_producto=id_producto).first()

        if not producto:
            return redirect(url_for("verListaProductos"))

        error = None

        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            precio = request.form.get("precio", "").strip()
            stock = request.form.get("stock", "").strip()

            error = validarProducto(nombre, precio, stock)

            if not error:
                producto.nombre = nombre
                producto.precio = float(precio)
                producto.stock = int(stock)
                db_cursor.commit()
                return redirect(url_for("verListaProductos"))

        return render_template("editar_producto.html", producto=producto, error=error)
    finally:
        db_cursor.close()


## Baja logica: no borramos la fila para no perder el historial del producto
def eliminarProducto(id_producto):
    db_cursor = Session()
    try:
        producto = db_cursor.query(Producto).filter_by(id_producto=id_producto).first()

        if producto:
            producto.activo = False
            db_cursor.commit()

        return redirect(url_for("verListaProductos"))
    finally:
        db_cursor.close()


def mostrarListaProducto():
    db_cursor = Session()
    try:
        productos = db_cursor.query(Producto).filter_by(activo=True).all()
        categorias = db_cursor.query(Categoria).all()
        return render_template("lista_productos.html", productos=productos, categorias=categorias)
    finally:
        db_cursor.close()


def reporte_stock_critico():
    db_cursor = Session()
    try:
        productos_criticos = (
            db_cursor.query(Producto)
            .filter(Producto.activo == True, Producto.stock <= 5)
            .all()
        )
        return render_template("stock_critico.html", productos=productos_criticos)
    finally:
        db_cursor.close()