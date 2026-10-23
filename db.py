from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship


motorDB = create_engine("sqlite:///ferreteriaJSJ.db")

Base = declarative_base()

Session = sessionmaker(bind=motorDB)


class Producto(Base):
    __tablename__ = "producto"

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

    ## para la clave foranea de categoria 
    fk_id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    ## esto es para relacionar las tablas producto y categoria
    categoria = relationship("Categoria")

class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)


class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    email = Column(String)
    telefono = Column(String)
    ## la baja es logica: el cliente deja de mostrarse pero se conserva su historial de compras
    activo = Column(Boolean, nullable=False, default=True)



### Funcion para crear la tablas

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
