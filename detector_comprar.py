from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import time

ARCHIVO_RESULTADOS = "resultados_comprar.html"
ARCHIVO_NUEVAS = "nuevas_licitaciones.html"
ARCHIVO_HISTORICO = "historico_comprar.txt"


def leer_historico():
    if not os.path.exists(ARCHIVO_HISTORICO):
        return set()

    with open(ARCHIVO_HISTORICO, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def guardar_historico(ids):
    with open(ARCHIVO_HISTORICO, "w", encoding="utf-8") as f:
        for x in sorted(ids):
            f.write(x + "\n")


def inicio_html(titulo):
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
    </head>
    <body style="font-family: Arial; background:#f4f4f4; padding:20px;">
        <h1>{titulo}</h1>
    """


def fin_html():
    return """
    </body>
    </html>
    """


options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 40)

driver.get("https://comprar.gob.ar/BuscarAvanzado.aspx")

campo = wait.until(
    EC.presence_of_element_located((By.ID, "ctl00_CPH1_txtNombrePliego"))
)

campo.clear()
campo.send_keys("libreria")

boton = wait.until(
    EC.element_to_be_clickable((By.ID, "ctl00_CPH1_btnListarPliegoAvanzado"))
)

boton.click()

wait.until(
    EC.presence_of_element_located((By.ID, "ctl00_CPH1_GridListaPliegos"))
)

time.sleep(3)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

tabla = soup.find("table", id="ctl00_CPH1_GridListaPliegos")

historico = leer_historico()
nuevo_historico = set(historico)

resultados = []
nuevas = []

if tabla:

    filas = tabla.find_all("tr")[1:]

    for fila in filas:

        celdas = fila.find_all("td")

        if len(celdas) >= 8:

            numero = celdas[0].get_text(" ", strip=True)
            expediente = celdas[1].get_text(" ", strip=True)

            link_tag = celdas[2].find("a")
            nombre = celdas[2].get_text(" ", strip=True)

            link = ""
            if link_tag and link_tag.get("href"):
                href = link_tag.get("href")

                if href.startswith("/"):
                    link = "https://comprar.gob.ar" + href
                else:
                    link = href

            tipo = celdas[3].get_text(" ", strip=True)
            apertura = celdas[4].get_text(" ", strip=True)
            estado = celdas[5].get_text(" ", strip=True)
            unidad = celdas[6].get_text(" ", strip=True)
            saf = celdas[7].get_text(" ", strip=True)

            if "adjudicado" in estado.lower():
                continue

            registro = f"""
            <div style="background:white; padding:15px; margin-bottom:15px; border-radius:10px;">
                <strong>Número:</strong> {numero}<br>
                <strong>Expediente:</strong> {expediente}<br>
                <strong>Nombre:</strong> {nombre}<br>
                <strong>Tipo:</strong> {tipo}<br>
                <strong>Apertura:</strong> {apertura}<br>
                <strong>Estado:</strong> {estado}<br>
                <strong>Unidad:</strong> {unidad}<br>
                <strong>SAF:</strong> {saf}<br><br>
                <a href="{link}" target="_blank" style="color:blue; font-weight:bold;">
                    🔗 Abrir licitación
                </a>
            </div>
            """

            resultados.append(registro)

            if numero not in historico:
                nuevas.append(registro)

            nuevo_historico.add(numero)

with open(ARCHIVO_RESULTADOS, "w", encoding="utf-8") as f:
    f.write(inicio_html("📋 Resultados generales COMPR.AR"))

    if resultados:
        f.writelines(resultados)
    else:
        f.write("<p>No se encontraron oportunidades vigentes.</p>")

    f.write(fin_html())

with open(ARCHIVO_NUEVAS, "w", encoding="utf-8") as f:
    f.write(inicio_html("🆕 Nuevas licitaciones detectadas"))

    if nuevas:
        f.writelines(nuevas)
    else:
        f.write("<p>No hay nuevas licitaciones.</p>")

    f.write(fin_html())

guardar_historico(nuevo_historico)

print("PROCESO TERMINADO")
print("Total vigentes detectadas:", len(resultados))
print("Nuevas:", len(nuevas))
print("Archivos HTML generados:")
print("-", ARCHIVO_RESULTADOS)
print("-", ARCHIVO_NUEVAS)