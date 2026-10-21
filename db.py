from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

motorDB = create_engine("sqlite:///ferreteria.jsj.db")

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

class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)



### Funcion para crear la tablas

def crearTablas():
    Base.metadata.create_all(motorDB)

    ## Esto es para hacer consultas a la BD
    db_cursor = Session()
    db_cursor.add(Categoria(nombre="Electronica"))
    db_cursor.commit()
    db_cursor.close()

crearTablas()