import requests
from bs4 import BeautifulSoup

url = "https://www.boletinoficial.gob.ar/seccion/tercera"

headers = {
    "User-Agent": "Mozilla/5.0"
}

respuesta = requests.get(url, headers=headers)

print("Estado:", respuesta.status_code)

soup = BeautifulSoup(respuesta.text, "html.parser")

links = soup.find_all("a")

print("\n--- LICITACIONES DETECTADAS ---\n")

for link in links:

    texto = link.get_text().strip()

    href = link.get("href")

    if texto and "licitación" in texto.lower():

        if href:

            if href.startswith("/"):

                href = "https://www.boletinoficial.gob.ar" + href

            print("📄", texto)
            print("🔗", href)
            print("----------------------------------")