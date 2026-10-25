from flask import request, render_template, redirect, url_for
from db import Session, Compra, DetalleCompra, Producto,Proveedor

def registrar_compra_proveedor(proveedor_id, items_comprados):
    db_cursor = Session()
    
    try:
        nueva_compra = Compra(fk_id_proveedor = proveedor_id)
        db_cursor.add(nueva_compra)
        db_cursor.flush()
        
        for item in items_comprados:
            
            detalle = DetalleCompra(
                fk_id_compra = nueva_compra.id_compra,
                fk_id_producto=item['producto_id'],
                cantidad=item['cantidad'],
                precio_compra=item['precio']
            )
            db_cursor.add(detalle)
            
            producto_db = db_cursor.query(Producto).filter_by(id_producto=item['producto_id']).first()
            if producto_db:
                producto_db.stock += item['cantidad']
                
        db_cursor.commit()
        return True, "Compra registrada y stock actualizado."
    
    except Exception as e:
        db_cursor.rollback() 
        return False, f"Ocurrió un error: {str(e)}"
    
    finally:
        db_cursor.close()
        
def cargar_formulario_compra(mensaje=""):
    db_cursor = Session()
    
    proveedores = db_cursor.query(Proveedor).all()
    productos = db_cursor.query(Producto).all()
    db_cursor.close()
    
    return render_template("agregar_compra.html", proveedores=proveedores, productos=productos, mensaje=mensaje)

def procesar_nueva_compra():
    db_cursor = Session()
    try: 
        id_prov = int(request.form["id_proveedor"])
        id_prod = int(request.form["id_producto"])
        cant = int(request.form["cantidad"])
        precio = float(request.form["precio_compra"])

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
        
        producto = db_cursor.query(Producto).filter_by(id_producto=id_prod).first()
        if producto:
            producto.stock += cant
            
        db_cursor.commit()
        return cargar_formulario_compra(mensaje="¡Compra registrada y stock actualizado con éxito!")

    except Exception as e:
        db_cursor.rollback()
        return cargar_formulario_compra(mensaje=f"Error al registrar: {str(e)}")
        
    finally:
        db_cursor.close()
        