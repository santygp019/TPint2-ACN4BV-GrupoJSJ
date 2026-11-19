import os
from dotenv import load_dotenv
from db import crearTablas, Session, Producto
from flask import Flask, render_template, request 
from producto import agregarProductos, mostrarListaProducto, reporte_stock_critico, editarProducto, eliminarProducto
from clientes import agregarCliente, editarCliente, darBajaCliente, ingresarCliente, verMiPerfil
from compras import cargar_formulario_compra, procesar_nueva_compra, historial_compras
from proveedores import agregarProveedor
from venta import ventaProducto, procesarCompraCatalogo, reporteVentas
from pedidos import pedidos_bp
from auth import auth_bp, requiere_rol
from api_dolar import obtener_cotizacion_dolar

load_dotenv()

app = Flask(__name__)  
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

app.register_blueprint(pedidos_bp)
app.register_blueprint(auth_bp)

crearTablas()

@app.context_processor
def inyectar_dolar():
    return dict(dolar=obtener_cotizacion_dolar())

@app.route("/")
def home():
    return render_template("index.html")

# --- RUTAS SOLO ADMINISTRADOR ---
@app.route("/agregar_productos", methods=["GET", "POST"])
@requiere_rol("administrador")
def cargarProducto():
    return agregarProductos()

@app.route("/editar_producto/<int:id_producto>", methods=["GET", "POST"])
@requiere_rol("administrador")
def modificarProducto(id_producto):
    return editarProducto(id_producto)

@app.route("/eliminar_producto/<int:id_producto>")
@requiere_rol("administrador")
def borrarProducto(id_producto):
    return eliminarProducto(id_producto)

@app.route("/clientes", methods=["GET", "POST"])
@requiere_rol("administrador")
def cargarCliente():
    return agregarCliente()

@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
@requiere_rol("administrador")
def modificarCliente(id_cliente):
    return editarCliente(id_cliente)

@app.route("/clientes/baja/<int:id_cliente>", methods=["POST"])
@requiere_rol("administrador")
def bajaCliente(id_cliente):
    return darBajaCliente(id_cliente)

@app.route("/compras/nueva", methods=["GET"])
@requiere_rol("administrador")
def ver_compras():
    return cargar_formulario_compra()

@app.route("/compras/nueva", methods=["POST"])
@requiere_rol("administrador")
def registrar_compras():
    return procesar_nueva_compra()

@app.route("/compras/historial", methods=["GET"])
@requiere_rol("administrador")
def ver_historial_compras():
    return historial_compras()

@app.route("/reportes/ventas", methods=["GET"])
@requiere_rol("administrador")
def ver_reporte_ventas():
    return reporteVentas()
    
@app.route("/proveedores", methods=["GET", "POST"])
@requiere_rol("administrador")
def cargarProveedor():
    return agregarProveedor()

# --- RUTAS ADMINISTRADOR Y EMPLEADO ---
@app.route("/lista_productos")
@requiere_rol("administrador", "empleado")
def verListaProductos():
    return mostrarListaProducto()

@app.route("/ventas", methods=["GET", "POST"])
@requiere_rol("administrador", "empleado")
def seccionVentas():
    return ventaProducto()

@app.route("/reportes/stock_critico")
@requiere_rol("administrador", "empleado")
def verStockCritico():
    return reporte_stock_critico()

# --- RUTAS CLIENTE Y PÚBLICAS ---
@app.route("/catalogo", methods=["GET", "POST"])
def catalogoCliente():
    return procesarCompraCatalogo()

@app.route("/ingresar", methods=["GET", "POST"])
def ingresar():
    return ingresarCliente()

@app.route("/mi_perfil", methods=["GET", "POST"])
@requiere_rol("cliente")
def miPerfil():
    return verMiPerfil()

@app.errorhandler(404)
def paginaNoEncontrada(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)