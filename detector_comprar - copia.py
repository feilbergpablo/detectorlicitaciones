from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

ARCHIVO = "resultados_comprar.txt"

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
    EC.presence_of_element_located((By.ID, "ctl00_CPH1_btnListarPliegoAvanzado"))
)

driver.execute_script("arguments[0].scrollIntoView(true);", boton)
time.sleep(1)
boton.click()

wait.until(
    EC.presence_of_element_located((By.ID, "ctl00_CPH1_lblCantidadListaPliegos"))
)

time.sleep(3)

with open(ARCHIVO, "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("RESULTADOS DETECTADOS:", ARCHIVO)

driver.quit()