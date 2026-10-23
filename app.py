from db import crearTablas
from flask import Flask
from producto import productos

app = Flask(__name__)

crearTablas()

@app.route("/", methods=["GET", "POST"])
def mostrarProducto():
    
    return productos()

if __name__ == "__main__":
    app.run(debug=True)