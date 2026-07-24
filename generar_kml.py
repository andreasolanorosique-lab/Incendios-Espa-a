import os
import csv
import requests
import xml.etree.ElementTree as ET

MAP_KEY = os.environ["FIRMS_MAP_KEY"]

SOURCE = "VIIRS_SNPP_NRT"

# España (aproximado)
BBOX = "-10,35,5,44"

URL = (
    f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
    f"{MAP_KEY}/{SOURCE}/{BBOX}/1"
)

print("Descargando incendios...")

r = requests.get(URL, timeout=120)
r.raise_for_status()

with open("fires.csv", "wb") as f:
    f.write(r.content)

print("CSV descargado.")

kml = ET.Element(
    "kml",
    xmlns="http://www.opengis.net/kml/2.2"
)

document = ET.SubElement(kml, "Document")

ET.SubElement(document, "name").text = "Incendios activos España"

print("Documento KML creado.")
# ==========================
# ESTILOS DEL KML
# ==========================

def crear_estilo(doc, nombre, color, escala):
    style = ET.SubElement(doc, "Style", id=nombre)

    icon_style = ET.SubElement(style, "IconStyle")

    ET.SubElement(icon_style, "scale").text = str(escala)

    ET.SubElement(icon_style, "color").text = color

    icon = ET.SubElement(icon_style, "Icon")

    ET.SubElement(
        icon,
        "href"
    ).text = "http://maps.google.com/mapfiles/kml/shapes/firedept.png"


crear_estilo(document, "frp_bajo", "ff00ffff", 1.8)
crear_estilo(document, "frp_medio", "ff00a5ff", 2.4)
crear_estilo(document, "frp_alto", "ff0060ff", 3.2)
crear_estilo(document, "frp_extremo", "ff0000ff", 4.0)


def obtener_estilo(frp):

    try:
        frp = float(frp)
    except:
        return "#frp_bajo"

    if frp < 10:
        return "#frp_bajo"

    if frp < 30:
        return "#frp_medio"

    if frp < 80:
        return "#frp_alto"

    return "#frp_extremo"
  # ==========================
# LEER CSV Y CREAR PUNTOS
# ==========================

with open("fires.csv", newline="", encoding="utf-8") as csvfile:

    lector = csv.DictReader(csvfile)

    total = 0

    for fila in lector:

        lat = fila.get("latitude")
        lon = fila.get("longitude")

        if not lat or not lon:
            continue

        frp = fila.get("frp", "0")

        placemark = ET.SubElement(document, "Placemark")

        ET.SubElement(
            placemark,
            "styleUrl"
        ).text = obtener_estilo(frp)

        nombre = (
            f"🔥 FRP {frp} MW"
        )

        ET.SubElement(
            placemark,
            "name"
        ).text = nombre

        descripcion = f"""
<![CDATA[
<h2>Incendio activo</h2>

<b>Fecha:</b> {fila.get('acq_date','')}<br>
<b>Hora:</b> {fila.get('acq_time','')}<br>
<b>Satélite:</b> {fila.get('satellite','')}<br>
<b>Instrumento:</b> {fila.get('instrument','')}<br>
<b>Confianza:</b> {fila.get('confidence','')}<br>
<b>FRP:</b> {frp} MW<br>

]]>
"""

        ET.SubElement(
            placemark,
            "description"
        ).text = descripcion

        punto = ET.SubElement(
            placemark,
            "Point"
        )

        ET.SubElement(
            punto,
            "coordinates"
        ).text = f"{lon},{lat},0"

        total += 1

print(f"{total} incendios añadidos al KML")
# ==========================
# GUARDAR EL KML
# ==========================

arbol = ET.ElementTree(kml)

try:
    ET.indent(arbol, space="  ")
except AttributeError:
    # Compatible con versiones antiguas de Python
    pass

arbol.write(
    "incendios_actual.kml",
    encoding="utf-8",
    xml_declaration=True
)

print("=" * 50)
print("KML generado correctamente")
print(f"Total de incendios: {total}")
print("Archivo: incendios_actual.kml")
print("=" * 50)
