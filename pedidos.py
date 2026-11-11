from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import Session, Producto, Cliente, Pedido, DetallePedido

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
def ver_pendientes():
    db_cursor = Session()
    try:
        # Filtramos solo los pedidos que aún no fueron entregados
        pedidos = db_cursor.query(Pedido).filter_by(estado="Pendiente de retiro").order_by(Pedido.fecha.asc()).all()
        return render_template("pedidos_pendientes.html", pedidos=pedidos)
    finally:
        db_cursor.close()

@pedidos_bp.route('/confirmar/<int:id_pedido>', methods=['POST'])
def confirmar_pedido(id_pedido):
    db_cursor = Session()
    try:
        pedido = db_cursor.query(Pedido).filter_by(id_pedido=id_pedido).first()
        if pedido:
            # Actualizamos el estado para sacarlo de la lista de pendientes
            pedido.estado = "Confirmado y Entregado"
            db_cursor.commit()
        return redirect(url_for('pedidos.ver_pendientes'))
    finally:
        db_cursor.close()