import requests
from datetime import datetime, timedelta

_cache_dolar = {
    "datos": None,
    "expira": datetime.min
}

def obtener_cotizacion_dolar():
    ahora = datetime.now()

    if _cache_dolar["datos"] and ahora < _cache_dolar["expira"]:
        return _cache_dolar["datos"]

    url = "https://dolarapi.com/v1/dolares/oficial"
    try:
        respuesta = requests.get(url, timeout=4)
        respuesta.raise_for_status()
        data = respuesta.json()

        cotizacion = {
            "compra": float(data.get("compra", 0)),
            "venta": float(data.get("venta", 0)),
            "fecha": data.get("fechaActualizacion", "")[:10],
            "disponible": True
        }

        _cache_dolar["datos"] = cotizacion
        _cache_dolar["expira"] = ahora + timedelta(minutes=10)
        return cotizacion

    except requests.exceptions.RequestException as e:
        print(f"Error al consultar DolarApi: {e}")
        return {
            "compra": None,
            "venta": None,
            "fecha": None,
            "disponible": False
        }