from flask import Flask
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

URL = "https://www.boletinoficial.gob.ar/seccion/tercera"
HEADERS = {"User-Agent": "Mozilla/5.0"}

PUNTAJES = {
    "impresor": 5,
    "toner": 5,
    "tóner": 5,
    "cartuch": 5,
    "fotocopiadora": 5,
    "notebook": 5,

    "resma": 4,
    "librer": 4,
    "útiles": 4,
    "monitor": 4,
    "hardware": 4,
    "scanner": 4,

    "papel": 2,
    "hojas": 2,

    "oficina": 1,
    "insumos": 1
}

ARCHIVO_HISTORICO = "resultados_insucom.txt"
ARCHIVO_NUEVOS = "nuevas_licitaciones.txt"


def leer_detalle(link):
    try:
        r = requests.get(link, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(" ", strip=True).lower()
    except:
        return ""


def cargar_historico():
    if not os.path.exists(ARCHIVO_HISTORICO):
        return set()

    with open(ARCHIVO_HISTORICO, "r", encoding="utf-8") as archivo:
        return set(archivo.readlines())


@app.route("/")
def home():

    try:
        historico = cargar_historico()

        r = requests.get(URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a")

        archivo_historico = open(ARCHIVO_HISTORICO, "w", encoding="utf-8")
        archivo_nuevos = open(ARCHIVO_NUEVOS, "w", encoding="utf-8")

        archivo_historico.write("RESULTADOS INSUCOM\n\n")
        archivo_nuevos.write("NUEVAS LICITACIONES DETECTADAS\n\n")

        html = """
        <h1>📄 Licitaciones - Sistema INSUCOM</h1>
        <p>🆕 = nueva | ⭐ Alta | 🟡 Media | 📄 Baja</p>
        <hr>
        """

        contador = 0

        for link in links:

            texto = link.get_text(strip=True)
            href = link.get("href")

            if texto and "licit" in texto.lower():

                if not href:
                    continue

                if href.startswith("/"):
                    href = "https://www.boletinoficial.gob.ar" + href

                detalle = leer_detalle(href)

                puntaje = 0
                coincidencias = []

                for palabra, puntos in PUNTAJES.items():

                    if palabra in detalle:
                        puntaje += puntos
                        coincidencias.append(palabra)

                # BONUS
                if "papel" in coincidencias and "resma" in coincidencias:
                    puntaje += 3

                if "impresor" in coincidencias and "toner" in coincidencias:
                    puntaje += 4

                if "librer" in coincidencias and "útiles" in coincidencias:
                    puntaje += 3

                if puntaje >= 8:
                    icono = "⭐"
                    prioridad = "Alta"
                elif puntaje >= 4:
                    icono = "🟡"
                    prioridad = "Media"
                else:
                    icono = "📄"
                    prioridad = "Baja"

                registro = (
                    f"{texto}\n"
                    f"Prioridad: {prioridad}\n"
                    f"Puntaje: {puntaje}\n"
                    f"Coincidencias: {', '.join(coincidencias) if coincidencias else 'ninguna'}\n"
                    f"Link: {href}\n"
                    f"{'-'*40}\n"
                )

                archivo_historico.write(registro)

                es_nueva = texto + "\n" not in historico

                if es_nueva:
                    archivo_nuevos.write(registro)
                    icono_nuevo = "🆕 "
                else:
                    icono_nuevo = ""

                html += f"""
                <p>
                    {icono_nuevo}{icono} <strong>{texto}</strong><br>
                    Prioridad: {prioridad} | Puntaje: {puntaje}<br>
                    Coincidencias: {", ".join(coincidencias) if coincidencias else "ninguna"}<br>
                    <a href="{href}" target="_blank">🔗 Abrir licitación</a>
                </p>
                <hr>
                """

                contador += 1

                if contador >= 15:
                    break

        archivo_historico.close()
        archivo_nuevos.close()

        return html

    except Exception as e:

        return f"<h1>⚠ Error</h1><p>{e}</p>"


if __name__ == "__main__":
    app.run(debug=True)