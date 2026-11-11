from flask import render_template, request, redirect, url_for
from db import Session, Producto, Cliente, Venta, DetalleVenta
from sqlalchemy import or_, cast, String  # Importamos herramientas para la búsqueda parcial

def ventaProducto():
    db_cursor = Session()
    try:
        if request.method == "POST":
            id_producto = request.form.get("id_producto")
            cantidad_vendida = int(request.form.get("cantidad"))
        
            producto = db_cursor.query(Producto).filter_by(id_producto=id_producto).first()

            if producto and producto.stock >= cantidad_vendida:
                ## Descontamos el stock
                producto.stock -= cantidad_vendida

                nueva_venta= Venta()
                db_cursor.add(nueva_venta)
                db_cursor.flush()### esto permite obtener el id de la venta antes del commit.

                detalle = DetalleVenta(
                    fk_id_venta = nueva_venta.id_venta,
                    fk_id_producto = producto.id_producto,
                    cantidad = cantidad_vendida,
                    precio_venta = producto.precio
                )
                db_cursor.add(detalle)
                db_cursor.commit()

                return redirect(url_for("seccionVentas"))
        
       
        # Atrapamos el texto que viene del formulario HTML
        texto_buscado = request.args.get("busqueda")
        
        # Armamos la consulta base (solo activos y con stock)
       # 2. Armamos la consulta base (ahora trae TODOS los activos, incluso con stock 0)
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
        # --- LÓGICA DE COMPRA (POST) ---
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
                
        # --- LÓGICA DEL BUSCADOR Y CATÁLOGO (GET) ---
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