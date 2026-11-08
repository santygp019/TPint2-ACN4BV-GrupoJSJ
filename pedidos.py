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