import requests
import xml.etree.ElementTree as ET

URL = (
    "https://services-eu1.arcgis.com/VC42ANIVJ5dUfvUn/"
    "ArcGIS/rest/services/Burned_Areas_EFFIS/FeatureServer/23/query"
)

PARAMS = {
    "where": "1=1",
    "outFields": "*",
    "returnGeometry": "true",
    "f": "geojson"
}

print("Descargando datos de Copernicus...")

respuesta = requests.get(URL, params=PARAMS, timeout=60)
respuesta.raise_for_status()

datos = respuesta.json()

print(f"Incendios descargados: {len(datos['features'])}")
kml = ET.Element(
    "kml",
    xmlns="http://www.opengis.net/kml/2.2"
)

documento = ET.SubElement(kml, "Document")

ET.SubElement(documento, "name").text = "Incendios España"

for elemento in datos["features"]:

    geometria = elemento.get("geometry")

    if not geometria:
        continue

    if geometria.get("type") != "Polygon":
        continue

    coordenadas = geometria["coordinates"][0]

    placemark = ET.SubElement(documento, "Placemark")

    ET.SubElement(placemark, "name").text = "Área quemada"

    polygon = ET.SubElement(placemark, "Polygon")

    outer = ET.SubElement(polygon, "outerBoundaryIs")

    ring = ET.SubElement(outer, "LinearRing")

    texto = ""

    for lon, lat in coordenadas:
        texto += f"{lon},{lat},0 "

    ET.SubElement(ring, "coordinates").text = texto.strip()
  arbol = ET.ElementTree(kml)

ET.indent(arbol, space="  ")

arbol.write(
    "incendios_actual.kml",
    encoding="utf-8",
    xml_declaration=True
)

print("Archivo incendios_actual.kml generado correctamente.")
