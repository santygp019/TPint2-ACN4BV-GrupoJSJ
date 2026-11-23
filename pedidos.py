from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import Session, Producto, Cliente, Pedido, DetallePedido, Venta, DetalleVenta
from auth import requiere_rol

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

@pedidos_bp.route('/catalogo', methods=['GET', 'POST'])


def catalogo_cliente():
    db_cursor = Session()
    try:
        if request.method == "POST":
            id_cliente = request.form.get("id_cliente")
            id_producto = request.form.get("id_producto")
            cantidad_pedida = int(request.form.get("cantidad"))

            producto = db_cursor.query(Producto).filter_by(id_producto=id_producto).first()

            if producto and producto.stock >= cantidad_pedida:
                producto.stock -= cantidad_pedida

                nuevo_pedido = Pedido(fk_id_cliente=id_cliente)
                db_cursor.add(nuevo_pedido)
                db_cursor.flush()

                detalle = DetallePedido(
                    fk_id_pedido=nuevo_pedido.id_pedido,
                    fk_id_producto=producto.id_producto,
                    cantidad=cantidad_pedida,
                    precio_unitario=producto.precio
                )
                db_cursor.add(detalle)
                db_cursor.commit()

                return redirect(url_for("pedidos.catalogo_cliente"))

        productos_disponibles = db_cursor.query(Producto).filter(Producto.activo == True, Producto.stock > 0).all()
        clientes = db_cursor.query(Cliente).filter_by(activo=True).all()

        return render_template("catalogo_cliente.html", productos=productos_disponibles, clientes=clientes)
    finally:
        db_cursor.close()


@pedidos_bp.route('/pendientes', methods=['GET'])
@requiere_rol("administrador", "empleado")


def ver_pendientes():
    db_cursor = Session()
    try:
        # Filtramos solo los pedidos que aún no fueron entregados
        pedidos = db_cursor.query(Pedido).filter_by(estado="Pendiente de retiro").order_by(Pedido.fecha.asc()).all()
        return render_template("pedidos_pendientes.html", pedidos=pedidos)
    finally:
        db_cursor.close()


@pedidos_bp.route('/confirmar/<int:id_pedido>', methods=['POST'])
@requiere_rol("administrador", "empleado")


def confirmar_pedido(id_pedido):
    db_cursor = Session()
    try:
        pedido = db_cursor.query(Pedido).filter_by(id_pedido=id_pedido).first()

        if pedido and pedido.estado == "Pendiente de retiro":
            # 1) crear la venta, a nombre del cliente del pedido
            nueva_venta = Venta(fk_id_cliente=pedido.fk_id_cliente)
            db_cursor.add(nueva_venta)
            db_cursor.flush()  # asegura que nueva_venta.id_venta esté disponible

            # 2) por cada producto del pedido, crear un detalle de venta
            for detalle in pedido.detalles:
                detalle_venta = DetalleVenta(
                    fk_id_venta=nueva_venta.id_venta,
                    fk_id_producto=detalle.fk_id_producto,
                    cantidad=detalle.cantidad,
                    precio_venta=detalle.precio_unitario
                )
                db_cursor.add(detalle_venta)

            # 3) cambiar el estado y guardar todo
            pedido.estado = "Confirmado y Entregado"
            
            db_cursor.commit()

            flash("Pedido confirmado: se registró la venta.")

    except Exception:
        # si algo falla, se deshace todo lo que se había hecho a medias
        db_cursor.rollback()
        flash("No se pudo confirmar el pedido. Probá de nuevo.")

    finally:
        db_cursor.close()

    return redirect(url_for('pedidos.ver_pendientes'))

@pedidos_bp.route('/rechazar/<int:id_pedido>', methods=['POST'])
@requiere_rol("administrador", "empleado")


def rechazar_pedido(id_pedido):
    db_cursor = Session()
    try:
        pedido = db_cursor.query(Pedido).filter_by(id_pedido=id_pedido).first()

        if pedido and pedido.estado == "Pendiente de retiro":
            # 1) devolver al stock lo que se había reservado
            stock_devueltos = 0

            for detalle in pedido.detalles:
                producto = db_cursor.query(Producto).filter_by(id_producto=detalle.fk_id_producto).first()
                if producto:
                    producto.stock += detalle.cantidad
                    stock_devueltos += detalle.cantidad

            # 2) cambiar el estado del pedido a "Rechazado"
            pedido.estado = "Rechazado"

            # 3) guardar los cambios en la base
            db_cursor.commit()

            if stock_devueltos == 1:
                flash("Pedido rechazado: se devolvió 1 unidad al stock.")
            else:
                flash("Pedido rechazado: se devolvieron " + str(stock_devueltos) + " unidades al stock.")

    except Exception:
        # si algo falla, se deshace todo lo que se había hecho a medias
        db_cursor.rollback()
        flash("No se pudo rechazar el pedido. Probá de nuevo.")

    finally:
        db_cursor.close()

    return redirect(url_for('pedidos.ver_pendientes'))

@pedidos_bp.route('/mis_pedidos', methods=['GET'])
@requiere_rol("cliente")
def mis_pedidos():
    # el cliente tiene que haber ingresado
    id_cliente = session.get("id_cliente")
    if not id_cliente:
        return redirect(url_for("ingresar"))

    db_cursor = Session()
    try:
        # traer solo los pedidos de ese cliente, del más nuevo al más viejo
        pedidos = db_cursor.query(Pedido).filter_by(fk_id_cliente=id_cliente).order_by(Pedido.fecha.desc()).all()
        return render_template("mis_pedidos.html", pedidos=pedidos)
    finally:
        db_cursor.close()