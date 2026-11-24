import os
from dotenv import load_dotenv
from db import crearTablas, Session, Producto, Pedido, Venta, DetalleVenta
from sqlalchemy import func
from datetime import datetime, timedelta
from flask import Flask, render_template, request, session
from producto import agregarProductos, mostrarListaProducto, reporte_stock_critico, editarProducto, eliminarProducto
from clientes import agregarCliente, editarCliente, darBajaCliente, verMiPerfil
from compras import cargar_formulario_compra, procesar_nueva_compra, historial_compras
from proveedores import agregarProveedor
from pedidos import pedidos_bp
from auth import auth_bp, requiere_rol, iniciar_google
from api_dolar import obtener_cotizacion_dolar
from werkzeug.middleware.proxy_fix import ProxyFix
from venta import ventaProducto, procesarCompraCatalogo, reporteVentas, ventasMostrador

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
iniciar_google(app)

app.register_blueprint(pedidos_bp)
app.register_blueprint(auth_bp)

crearTablas()

@app.context_processor
def inyectar_dolar():
    return dict(dolar=obtener_cotizacion_dolar())

@app.template_filter("hora_ar")
def hora_ar(fecha):
    # la base guarda la fecha en UTC: se muestra en hora argentina (UTC-3)
    if not fecha:
        return ""
    return (fecha - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")

@app.route("/")
def home():
    resumen = None

    # los números del panel solo se calculan para admin y empleado
    if session.get("rol") in ["administrador", "empleado"]:
        db_cursor = Session()
        try:
            # inicio del día de hoy en Argentina (la base guarda en UTC, 3 horas adelantada)
            ahora_ar = datetime.utcnow() - timedelta(hours=3)
            inicio_dia_ar = ahora_ar.replace(hour=0, minute=0, second=0, microsecond=0)
            inicio_utc = inicio_dia_ar + timedelta(hours=3)

            pedidos_pendientes = db_cursor.query(Pedido).filter_by(estado="Pendiente de retiro").count()

            ventas_hoy = db_cursor.query(Venta).filter(Venta.fecha >= inicio_utc).count()

            total_hoy = db_cursor.query(func.sum(DetalleVenta.cantidad * DetalleVenta.precio_venta)) \
                .join(Venta, Venta.id_venta == DetalleVenta.fk_id_venta) \
                .filter(Venta.fecha >= inicio_utc).scalar() or 0

            resumen = {
                "pedidos_pendientes": pedidos_pendientes,
                "ventas_hoy": ventas_hoy,
                "total_hoy": total_hoy
            }
        except Exception:
            # si falla la consulta, el panel igual se muestra (sin números)
            resumen = None
        finally:
            db_cursor.close()

    return render_template("index.html", resumen=resumen)

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

@app.route("/ventas/mostrador", methods=["GET"])
@requiere_rol("administrador", "empleado")
def verVentasMostrador():
    return ventasMostrador()


@app.route("/reportes/stock_critico")
@requiere_rol("administrador", "empleado")
def verStockCritico():
    return reporte_stock_critico()

# --- RUTAS CLIENTE Y PÚBLICAS ---
@app.route("/catalogo", methods=["GET", "POST"])
def catalogoCliente():
    return procesarCompraCatalogo()


@app.route("/mi_perfil", methods=["GET", "POST"])
@requiere_rol("cliente")
def miPerfil():
    return verMiPerfil()

@app.errorhandler(404)
def paginaNoEncontrada(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)