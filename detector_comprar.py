from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import time

ARCHIVO_RESULTADOS = "resultados_comprar.txt"
ARCHIVO_NUEVAS = "nuevas_licitaciones.txt"
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
        celdas = [c.get_text(" ", strip=True) for c in fila.find_all("td")]

        if len(celdas) >= 8:
            numero = celdas[0]
            expediente = celdas[1]
            nombre = celdas[2]
            tipo = celdas[3]
            apertura = celdas[4]
            estado = celdas[5]
            unidad = celdas[6]
            saf = celdas[7]

            registro = f"""Número: {numero}
Expediente: {expediente}
Nombre: {nombre}
Tipo: {tipo}
Apertura: {apertura}
Estado: {estado}
Unidad: {unidad}
SAF: {saf}
{"-" * 70}
"""

            resultados.append(registro)

            if numero not in historico:
                nuevas.append(registro)

            nuevo_historico.add(numero)

with open(ARCHIVO_RESULTADOS, "w", encoding="utf-8") as f:
    f.write("RESULTADOS COMPR.AR - LIBRERIA\n\n")
    f.writelines(resultados)

with open(ARCHIVO_NUEVAS, "w", encoding="utf-8") as f:
    f.write("NUEVAS LICITACIONES DETECTADAS\n\n")
    if nuevas:
        f.writelines(nuevas)
    else:
        f.write("No hay nuevas licitaciones.\n")

guardar_historico(nuevo_historico)

print("PROCESO TERMINADO")
print("Total detectadas:", len(resultados))
print("Nuevas:", len(nuevas))
print("Archivos actualizados:", ARCHIVO_RESULTADOS, ARCHIVO_NUEVAS)