from flask import request, render_template, redirect, url_for
from db import Session, Proveedor

def agregarProveedor():
    db_cursor = Session()

    if request.method == "POST":
        nombre_proveedor = request.form["nombre"].strip()
        
        # Validamos que no envíen el campo vacío
        if nombre_proveedor:
            nuevo_proveedor = Proveedor(nombre=nombre_proveedor)
            db_cursor.add(nuevo_proveedor)
            db_cursor.commit()
            
        db_cursor.close()
        
        return redirect(url_for("cargarProveedor"))
    
    proveedores = db_cursor.query(Proveedor).all()
    db_cursor.close()
    
    return render_template("agregar_proveedor.html", proveedores=proveedores)