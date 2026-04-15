import requests
from bs4 import BeautifulSoup
import time
import os

# =========================
# CONFIGURACIÓN
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS").split(",")

URL = "https://shop.gmm-tv.com/"
CHECK_INTERVAL = 60  # segundos

ARCHIVO_ESTADO = "estado_inicial.txt"

# =========================
# TELEGRAM
# =========================
def enviar_mensaje(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for chat_id in CHAT_IDS:
        data = {
            "chat_id": chat_id,
            "text": mensaje
        }
        requests.post(url, data=data)

# =========================
# SCRAPER
# =========================
def obtener_productos():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    productos = []

    items = soup.find_all("div")

    for item in items:
        texto = item.get_text(separator=" ").strip()

        if "฿" in texto:
            nombre = texto.split("\n")[0].strip()
            estado = texto.upper()

            if "OUT OF STOCK" in estado:
                en_stock = False
            elif "AWAITING STOCK" in estado:
                en_stock = False
            elif "IN STOCK" in estado:
                en_stock = True
            else:
                continue

            productos.append({
                "nombre": nombre,
                "link": URL,
                "en_stock": en_stock
            })

    return productos

# =========================
# MONITOR
# =========================
def monitor():
    print("Iniciando monitor GMMTV...")
    estado_anterior = {}

    while True:
        try:
            productos = obtener_productos()
            print(f"Productos detectados: {len(productos)}")

            disponibles = []

            for p in productos:
                nombre = p["nombre"]
                en_stock = p["en_stock"]

                if nombre not in estado_anterior:
                    estado_anterior[nombre] = en_stock
                    continue

                if not estado_anterior[nombre] and en_stock:
                    disponibles.append(p)

                estado_anterior[nombre] = en_stock

            if len(disponibles) == 1:
                p = disponibles[0]
                mensaje = f"🔥 {p['nombre']} está de nuevo en stock!\n{p['link']}"
                enviar_mensaje(mensaje)

            elif len(disponibles) > 1:
                mensaje = "🔥 Algunos productos volvieron a estar en stock:\n\n"
                for p in disponibles:
                    mensaje += f"- {p['nombre']}\n"

                mensaje += f"\nVer tienda: {URL}"
                enviar_mensaje(mensaje)

        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_INTERVAL)

# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    enviar_mensaje("🚀 Monitor iniciado correctamente")
    monitor()
