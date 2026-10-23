from db import crearTablas
from flask import Flask, render_template
from producto import agregarProductos, mostrarListaProducto

app = Flask(__name__)

crearTablas()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/agregar_productos", methods=["GET", "POST"])
def cargarProducto():

    return agregarProductos()


@app.route("/lista_productos")
def verListaProductos():

    return mostrarListaProducto()


if __name__ == "__main__":
    app.run(debug=True)