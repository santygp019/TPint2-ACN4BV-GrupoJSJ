from flask import render_template, request, redirect, url_for, flash
from db import Session, Producto, Cliente, Venta, DetalleVenta
from sqlalchemy import or_, cast, String, func, desc
from datetime import datetime, timedelta

def ventaProducto():
    db_cursor = Session()
    try:
        if request.method == "POST":
            id_producto = request.form.get("id_producto")

            try:
                cantidad_vendida = int(request.form.get("cantidad"))
            except (ValueError, TypeError):
                flash("La cantidad tiene que ser un número entero.")
                return redirect(url_for("seccionVentas"))

            if cantidad_vendida <= 0:
                flash("La cantidad tiene que ser mayor a cero.")
                return redirect(url_for("seccionVentas"))

            producto = db_cursor.query(Producto).filter_by(id_producto=id_producto).first()

            if producto and producto.stock >= cantidad_vendida:
                ## Descontamos el stock
                producto.stock -= cantidad_vendida

                nueva_venta = Venta()
                db_cursor.add(nueva_venta)
                db_cursor.flush()  # esto permite obtener el id de la venta antes del commit.

                detalle = DetalleVenta(
                    fk_id_venta=nueva_venta.id_venta,
                    fk_id_producto=producto.id_producto,
                    cantidad=cantidad_vendida,
                    precio_venta=producto.precio
                )
                db_cursor.add(detalle)
                db_cursor.commit()

                flash("Venta registrada: se descontaron " + str(cantidad_vendida) + " unidades del stock.")
                return redirect(url_for("seccionVentas"))

            flash("No hay stock suficiente o el producto no existe.")
            return redirect(url_for("seccionVentas"))

        # Atrapamos el texto que viene del formulario HTML
        texto_buscado = request.args.get("busqueda")

        # Armamos la consulta base (trae TODOS los activos, incluso con stock 0)
        query = db_cursor.query(Producto).filter(Producto.activo == True)

        # Si el usuario escribió algo, le agregamos el filtro de coincidencias parciales
        if texto_buscado:
            query = query.filter(
                or_(
                    Producto.nombre.ilike(f"%{texto_buscado}%"),
                    cast(Producto.id_producto, String).ilike(f"%{texto_buscado}%")
                )
            )

        # Ejecutamos la consulta final
        productoDisponible = query.all()

        clientes = db_cursor.query(Cliente).filter_by(activo=True).all()

        return render_template("ventas.html", productos=productoDisponible, clientes=clientes)
    finally:
        db_cursor.close()

def procesarCompraCatalogo():
    db_cursor = Session()
    try:
        #LÓGICA DE COMPRA (POST)
        if request.method == "POST":
            id_producto = request.form.get("id_producto")
            cantidad_comprada = int(request.form.get("cantidad"))
            
            producto = db_cursor.query(Producto).filter_by(id_producto=id_producto).first()
            
            if producto and producto.stock >= cantidad_comprada:
                producto.stock -= cantidad_comprada
                
                nueva_venta = Venta()
                db_cursor.add(nueva_venta)
                db_cursor.flush()
                
                detalle = DetalleVenta(
                    fk_id_venta=nueva_venta.id_venta,
                    fk_id_producto=producto.id_producto,
                    cantidad=cantidad_comprada,
                    precio_venta=producto.precio
                )
                db_cursor.add(detalle)
                db_cursor.commit()
                
                return redirect(url_for("catalogoCliente"))
                
        #LÓGICA DEL BUSCADOR Y CATÁLOGO (GET)
        texto_buscado = request.args.get("busqueda")
        query = db_cursor.query(Producto).filter(Producto.activo == True, Producto.stock > 0)
        
        if texto_buscado:
            query = query.filter(
                or_(
                    Producto.nombre.ilike(f"%{texto_buscado}%"),
                    cast(Producto.id_producto, String).ilike(f"%{texto_buscado}%")
                )
            )
            
        productos = query.all()
        return render_template("catalogo.html", productos=productos)
    finally:
        db_cursor.close()


def reporteVentas():
    db_cursor = Session()
    try:
        periodo = request.args.get("periodo", "todos")
        fecha_limite = None
        ahora = datetime.now()

        if periodo == "dia":
            fecha_limite = ahora - timedelta(days=1)
        elif periodo == "semana":
            fecha_limite = ahora - timedelta(weeks=1)
        elif periodo == "mes":
            fecha_limite = ahora - timedelta(days=30)

        query = db_cursor.query(
            Producto.nombre,
            func.sum(DetalleVenta.cantidad).label('total_vendido'),
            func.sum(DetalleVenta.cantidad * DetalleVenta.precio_venta).label('ingreso_total')
        ).join(DetalleVenta, Producto.id_producto == DetalleVenta.fk_id_producto)\
         .join(Venta, Venta.id_venta == DetalleVenta.fk_id_venta)

        if fecha_limite:
            query = query.filter(Venta.fecha >= fecha_limite)

        resultados = query.group_by(Producto.id_producto)\
                          .order_by(desc('total_vendido')).all()

        return render_template("reporte_ventas.html", resultados=resultados, periodo_actual=periodo)
    finally:
        db_cursor.close()