import requests
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode

api_key = ''
api_secret = ''
base_url = 'https://api.binance.com'
endpoint = '/sapi/v1/simple-earn/flexible/list'


def formatear_producto(producto):
    asset = producto.get('asset')
    apr = float(producto.get('latestAnnualPercentageRate', 0)) * 100
    status = producto.get('status')
    min_compra = producto.get('minPurchaseAmount')
    puede_comprar = producto.get('canPurchase')
    niveles = producto.get('tierAnnualPercentageRate', {})

    niveles_str = "\n".join([f"  {rango}: {float(tasa)*100:.2f}%" for rango, tasa in niveles.items()]) if niveles else "N/A"

    return {
        'Cripto': asset,
        'APR anual (%)': round(apr, 4),
        'Estado': status,
        'Monto mínimo compra': min_compra,
        'Puede comprar': puede_comprar,
        'Niveles APR (%) por rango': niveles_str
    }

def obtener_todos_productos():
    todos_productos = []
    pagina = 1
    tamaño_pagina = 100
    total_esperado = None

    while True:
        params = {
            'timestamp': int(time.time() * 1000),
            'current': pagina,
            'size': tamaño_pagina
        }
        query_string = urlencode(params)
        signature = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
        headers = {'X-MBX-APIKEY': api_key}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Error en la consulta:", response.status_code, response.text)
            break

        data = response.json()
        if total_esperado is None:
            total_esperado = data.get('total', 0)

        productos = data.get('rows', [])
        todos_productos.extend(productos)

        if len(todos_productos) >= total_esperado:
            break
        pagina += 1

    return todos_productos

def main():
    productos = obtener_todos_productos()
    productos_ordenados = sorted(productos, key=lambda x: float(x.get('latestAnnualPercentageRate', 0)), reverse=True)
    productos_formateados = [formatear_producto(p) for p in productos_ordenados]

    # Mostrar datos legibles
    for p in productos_formateados:
        for k, v in p.items():
            print(f"{k}: {v}")
        print("-" * 40)

    # Guardar a JSON
    with open('productos_binance_earn_ordenados.json', 'w', encoding='utf-8') as f:
        json.dump(productos_formateados, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
