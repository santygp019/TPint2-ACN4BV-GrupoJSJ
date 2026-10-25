from flask import Flask, request, render_template, redirect, url_for
from db import Session, Producto, Categoria

## Valida los datos del formulario, devuelve un mensaje de error o None si esta todo bien
def validarProducto(nombre, precio, stock):
    if not nombre:
        return "El nombre es obligatorio."

    if not precio or not stock:
        return "El precio y el stock no pueden estar vacios"

    if float(precio) <= 0 or int(stock) <=0:
        return "El precio o el stock no pueden ser igual a 0"

    return None



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

def editarProducto(id_producto):
    db_cursor = Session()
    producto = db_cursor.query(Producto).filter_by(id_producto=id_producto).first()

    if not producto:
        db_cursor.close()
        return redirect(url_for("cargarProducto"))

    error = None

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        precio = request.form["precio"].strip()
        stock = request.form["stock"].strip()

        error = validarProducto(nombre, precio, stock)

        if not error:
            producto.nombre = nombre
            producto.precio = float(precio)
            producto.stock = int(stock)
            db_cursor.commit()
            db_cursor.close()

            return redirect(url_for("cargarProducto"))

    pagina = render_template("editar_producto.html", producto=producto, error=error)
    db_cursor.close()

    return pagina





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