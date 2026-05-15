from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

ARCHIVO_TXT = "resultados_comprar.txt"
ARCHIVO_HTML = "resultados_comprar.html"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 40)

driver.get("https://comprar.gob.ar/BuscarAvanzado.aspx")

# Buscar libreria
campo = wait.until(
    EC.presence_of_element_located((By.ID, "ctl00_CPH1_txtNombrePliego"))
)

campo.clear()
campo.send_keys("libreria")

boton = wait.until(
    EC.element_to_be_clickable((By.ID, "ctl00_CPH1_btnListarPliegoAvanzado"))
)

driver.execute_script("arguments[0].scrollIntoView(true);", boton)
time.sleep(1)
boton.click()

wait.until(
    EC.presence_of_element_located((By.ID, "ctl00_CPH1_lblCantidadListaPliegos"))
)

time.sleep(4)

# Más preciso: cada resultado suele estar en paneles con texto útil
bloques = driver.find_elements(By.CSS_SELECTOR, "div.caja-resultados, div.panel, div.row")

resultados_txt = "RESULTADOS COMPR.AR - SOLO OPORTUNIDADES VIGENTES\n\n"

html = """
<html>
<head>
<meta charset="UTF-8">
<title>📋 Resultados generales COMPR.AR</title>
</head>
<body style="font-family: Arial; background:#f4f4f4; padding:20px;">
<h1>📋 Resultados generales COMPR.AR</h1>
"""

contador = 0
vistos = set()

for bloque in bloques:
    texto = bloque.text.strip()

    # Vacío
    if not texto:
        continue

    # Basura paginación
    if "1 2 3 4 5" in texto or "..." in texto and "Número:" in texto and len(texto) < 120:
        continue

    # Tiene que ser resultado real
    if "Número:" not in texto:
        continue

    # Evitar duplicados
    if texto in vistos:
        continue

    vistos.add(texto)

    # Excluir cerradas
    if "Adjudicado" in texto or "Finalizado" in texto:
        continue

    # Buscar link real
    link_real = ""

    links = bloque.find_elements(By.TAG_NAME, "a")

    for l in links:
        href = l.get_attribute("href")

        if not href:
            continue

        # Ignorar paginación javascript
        if "javascript" in href.lower():
            continue

        # Link válido COMPR.AR
        if "comprar.gob.ar" in href.lower():
            link_real = href
            break

    # Si no encontró en el bloque, buscar dentro del HTML interno
    if not link_real:
        try:
            html_interno = bloque.get_attribute("innerHTML")
            import re
            match = re.search(r'https://comprar\.gob\.ar[^"\']+', html_interno)
            if match:
                link_real = match.group(0)
        except:
            pass

    resultados_txt += texto + "\n"

    if link_real:
        resultados_txt += f"Link: {link_real}\n"

    resultados_txt += "-" * 60 + "\n"

    html += f"""
    <div style="background:white; padding:15px; margin-bottom:15px; border-radius:10px;">
        {texto.replace(chr(10), "<br>")}
    """

    if link_real:
        html += f"""
        <br><br>
        <a href="{link_real}" target="_blank" style="color:blue; font-weight:bold; font-size:18px;">
            🔗 Abrir licitación
        </a>
        """

    html += "</div>"

    contador += 1

with open(ARCHIVO_TXT, "w", encoding="utf-8") as f:
    f.write(resultados_txt)

html += """
</body>
</html>
"""

with open(ARCHIVO_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("PROCESO TERMINADO")
print("Total vigentes detectadas:", contador)

driver.quit()