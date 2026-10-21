from flask import Flask, render_template, request, redirect, url_for
from db import Session, Producto, Categoria, crearTablas


app = Flask(__name__)

crearTablas()


@app.route("/", method=["GET", "POST"])

def productos():
    db_cursor = Session()

    ## capturamos nuestro formulario 
    if request.method == "POST":

## aca instanciamos un nuevo producto donde cada valor viene del formulario        
        nuevo_producto = Producto(
            nombre = request.form["nombre"],
            precio = request.form["precio"],
            stock = request.form["stock"],
            fk_id_categoria = request.form["id_categoria"]
        )
        ## Lo agregamos, hacemos commit y cerramos 
        db_cursor.add(nuevo_producto)
        db_cursor.commit()
        db_cursor.close()

        return redirect(url_for("Productos"))


    productos =  db_cursor.query(Producto).all()
    categorias = db_cursor.query(Categoria).all() ## Esto es igual a hacer un select * from categoria
    
    return render_template("productos.html", productos=productos, categorias=categorias)

if __name__ == "__main__":
    app.run(debug=True)