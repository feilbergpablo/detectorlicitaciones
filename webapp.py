from flask import Flask

app = Flask(__name__)

ARCHIVO_RESULTADOS = "resultados_comprar.txt"
ARCHIVO_NUEVAS = "nuevas_licitaciones.txt"


def leer_archivo(nombre):
    try:
        with open(nombre, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Sin datos disponibles."


@app.route("/")
def home():

    nuevas = leer_archivo(ARCHIVO_NUEVAS)

    html = f"""
    <html>
    <head>
        <title>Detector COMPR.AR PRO</title>
    </head>
    <body style="font-family: Arial; margin: 30px; background:#f4f4f4;">
    
        <h1>📄 Detector COMPR.AR PRO</h1>

        <h2>🆕 Nuevas licitaciones detectadas</h2>

        <pre style="
            white-space: pre-wrap;
            background: white;
            padding: 15px;
            border-radius: 8px;
            border:1px solid #ccc;
            font-size:16px;
        ">{nuevas}</pre>

        <p>
            <a href="/resultados">
                📊 Ver resultados generales / análisis completo
            </a>
        </p>

    </body>
    </html>
    """

    return html


@app.route("/resultados")
def resultados():

    datos = leer_archivo(ARCHIVO_RESULTADOS)

    return f"""
    <html>
    <head>
        <title>Resultados generales COMPR.AR</title>
    </head>
    <body style="font-family: Arial; margin: 30px; background:#f4f4f4;">

        <h1>📋 Resultados generales / Análisis completo COMPR.AR</h1>

        <pre style="
            white-space: pre-wrap;
            background: white;
            padding: 15px;
            border-radius: 8px;
            border:1px solid #ccc;
            font-size:16px;
        ">{datos}</pre>

        <p>
            <a href="/">⬅ Volver</a>
        </p>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)