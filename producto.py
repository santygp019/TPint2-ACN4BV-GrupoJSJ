from flask import Flask, request, render_template, redirect, url_for
from db import Session, Producto, Categoria


def agregarProductos():
    db_cursor = Session()

    ## capturamos nuestro formulario 
    if request.method == "POST":

        nuevo_producto = Producto(
            nombre = request.form["nombre"],
            precio =float(request.form["precio"]),
            stock =int(request.form["stock"]),
            fk_id_categoria = int(request.form["id_categoria"])
        )
        ## Lo agregamos, hacemos commit y cerramos 
        db_cursor.add(nuevo_producto)
        db_cursor.commit()
        db_cursor.close()

        return redirect(url_for("cargarProducto"))

 
    productos =  db_cursor.query(Producto).all()
    categorias = db_cursor.query(Categoria).all() ## Esto es igual a hacer un select * from categoria
    return render_template("agregar_productos.html", productos=productos, categorias=categorias)


def mostrarListaProducto():
    db_cursor = Session()

    productos = db_cursor.query(Producto).all()

    return render_template("lista_productos.html", productos=productos)

def reporte_stock_critico():
    db_cursor = Session()
    productos_criticos = db_cursor.query(Producto).filter(Producto.stock <= 5).all()
    
    pagina_html = render_template("stock_critico.html", productos=productos_criticos)
    db_cursor.close()
    
    return pagina_html