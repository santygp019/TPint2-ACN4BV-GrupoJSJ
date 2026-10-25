from db import crearTablas, Session, Producto
from flask import Flask, render_template
from producto import agregarProductos, mostrarListaProducto, reporte_stock_critico, editarProducto, eliminarProducto
from clientes import agregarCliente, editarCliente, darBajaCliente
from compras import cargar_formulario_compra, procesar_nueva_compra
from proveedores import agregarProveedor

app = Flask(__name__)

crearTablas()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/agregar_productos", methods=["GET", "POST"])
def cargarProducto():

    return agregarProductos()

@app.route("/editar_producto/<int:id_producto>", methods=["GET", "POST"])
def modificarProducto(id_producto):

    return editarProducto(id_producto)

@app.route("/eliminar_producto/<int:id_producto>")
def borrarProducto(id_producto):

    return eliminarProducto(id_producto)


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



@app.route("/compras/nueva", methods=["GET"])
def ver_compras():
    return cargar_formulario_compra()

@app.route("/compras/nueva", methods=["POST"])
def registrar_compras():
    return procesar_nueva_compra()


@app.route("/reportes/stock_critico")
def verStockCritico():
    return reporte_stock_critico()
    
@app.route("/proveedores", methods=["GET", "POST"])
def cargarProveedor():
    return agregarProveedor()




if __name__ == "__main__":
    app.run(debug=True)
