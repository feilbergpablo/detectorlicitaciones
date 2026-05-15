import requests
from bs4 import BeautifulSoup
import os
import unicodedata

URLS = [
    "https://comprar.gob.ar/BuscarAvanzado.aspx",
    "https://comprar.gob.ar/BuscarAvanzadoPublicacion.aspx",
    "https://www.boletinoficial.gob.ar/seccion/tercera"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

PALABRAS_CLAVE = [
    "libreria", "librería",
    "utiles", "útiles",
    "papeleria", "papelería",
    "resma", "resmas",
    "papel", "hojas",
    "oficina", "insumos",
    "toner", "tóner",
    "impresora", "impresoras",
    "cartucho", "cartuchos",
    "computacion", "computación",
    "notebook", "scanner",
    "elementos de libreria",
    "articulos de libreria",
    "útiles de oficina"
]

ARCHIVO_HISTORICO = "resultados_insucom.txt"
ARCHIVO_NUEVOS = "nuevas_licitaciones.txt"


def limpiar(texto):
    texto = texto.lower()
    return ''.join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def coincide(texto):
    texto_limpio = limpiar(texto)
    return any(limpiar(palabra) in texto_limpio for palabra in PALABRAS_CLAVE)


def cargar_historico():
    if not os.path.exists(ARCHIVO_HISTORICO):
        return set()

    with open(ARCHIVO_HISTORICO, "r", encoding="utf-8") as archivo:
        return set(archivo.readlines())


def extraer_de_url(url):
    resultados = []

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        filas = soup.find_all("tr")

        if filas:
            for fila in filas:
                texto = fila.get_text(" ", strip=True)
                if texto and coincide(texto):
                    resultados.append((texto, url))

        links = soup.find_all("a")

        for link in links:
            texto = link.get_text(" ", strip=True)
            href = link.get("href")

            if texto and coincide(texto):
                if href:
                    if href.startswith("/"):
                        if "boletinoficial" in url:
                            href = "https://www.boletinoficial.gob.ar" + href
                        else:
                            href = "https://comprar.gob.ar" + href
                else:
                    href = url

                resultados.append((texto, href))

    except Exception as e:
        resultados.append((f"ERROR leyendo {url}: {e}", url))

    return resultados


def main():
    historico = cargar_historico()

    archivo_historico = open(ARCHIVO_HISTORICO, "w", encoding="utf-8")
    archivo_nuevos = open(ARCHIVO_NUEVOS, "w", encoding="utf-8")

    archivo_historico.write("RESULTADOS INSUCOM\n\n")
    archivo_nuevos.write("NUEVAS LICITACIONES DETECTADAS\n\n")

    total_detectadas = 0
    nuevas_detectadas = 0
    vistos = set()

    for url in URLS:
        resultados = extraer_de_url(url)

        for texto, link in resultados:
            clave = limpiar(texto + link)

            if clave in vistos:
                continue

            vistos.add(clave)

            registro = (
                f"{texto}\n"
                f"Link/Fuente: {link}\n"
                f"{'-' * 80}\n"
            )

            archivo_historico.write(registro)

            if registro not in historico:
                archivo_nuevos.write(registro)
                nuevas_detectadas += 1

            total_detectadas += 1

    archivo_historico.close()
    archivo_nuevos.close()

    print("===================================")
    print("DETECTOR INSUCOM FINALIZADO")
    print("Licitaciones detectadas:", total_detectadas)
    print("Nuevas detectadas:", nuevas_detectadas)
    print("Archivo generado:", ARCHIVO_NUEVOS)
    print("===================================")


if __name__ == "__main__":
    main()