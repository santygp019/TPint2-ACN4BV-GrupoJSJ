from db import crearTablas
from flask import Flask, render_template
from producto import agregarProductos, mostrarListaProducto
from clientes import agregarCliente, editarCliente, darBajaCliente

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


@app.route("/clientes", methods=["GET", "POST"])
def cargarCliente():

    return agregarCliente()


@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
def modificarCliente(id_cliente):

    return editarCliente(id_cliente)


@app.route("/clientes/baja/<int:id_cliente>", methods=["POST"])
def bajaCliente(id_cliente):

    return darBajaCliente(id_cliente)


if __name__ == "__main__":
    app.run(debug=True)

