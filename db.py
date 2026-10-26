from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean, DateTime,func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


motorDB = create_engine("sqlite:///ferreteriaJSJ.db")

Base = declarative_base()
### se le agrego el expire debido a que se pierden los datos al hacer la consulta y me daba error la categoria
Session = sessionmaker(bind=motorDB, expire_on_commit=False)


class Producto(Base):
    __tablename__ = "producto"

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True)

    ## para la clave foranea de categoria 
    fk_id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    ## esto es para relacionar las tablas producto y categoria
    categoria = relationship("Categoria")

class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)

class Venta(Base):
    __tablename__ = "venta"

    id_venta = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, default=func.now())
    fk_id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=True)

class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    fk_id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    fk_id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    ### Aca guardamos el precio de la venta por si en un futuro el precio aumenta el historial no se modifica
    precio_venta = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")

class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    email = Column(String)
    telefono = Column(String)
    ## la baja es logica: el cliente deja de mostrarse pero se conserva su historial de compras
    activo = Column(Boolean, nullable=False, default=True)

class Proveedor(Base):
    __tablename__ = "proveedor"
    
    id_proveedor = Column(Integer,primary_key=True,autoincrement=True )
    nombre = Column(String, nullable=False)
    
class Compra(Base):
    __tablename__ = "compra"
    
    id_compra = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(DateTime, default=func.now())
    fk_id_proveedor = Column(Integer, ForeignKey("proveedor.id_proveedor"),nullable=False)

    Proveedor = relationship("Proveedor")
    detalles = relationship("DetalleCompra", back_populates="compra")
### Funcion para crear la tablas

class DetalleCompra(Base):
    __tablename__ = "detalle_compra"
    
    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    fk_id_compra = Column(Integer, ForeignKey("compra.id_compra"), nullable=False)
    fk_id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_compra = Column(Float, nullable=False)
    
    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto")
    
def crearTablas():
    Base.metadata.create_all(motorDB)

    db_cursor = Session()
    categoria_existente = (
        db_cursor.query(Categoria).filter_by(nombre="Electronica").first()
    )
    ## Esto es para hacer consultas a la BD
    
    if not categoria_existente:
        db_cursor.add(Categoria(nombre="Electronica"))
        db_cursor.commit()
    db_cursor.close()
