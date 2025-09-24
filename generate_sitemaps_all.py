import pandas as pd
import os
import glob
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://ideazite.com"
SITEMAPS_DIR = os.path.join(BASE_DIR, "sitemaps")
os.makedirs(SITEMAPS_DIR, exist_ok=True)

# Buscar todos los CSV que terminan en _permalinks.csv (en subcarpetas)
csv_files = glob.glob(os.path.join(BASE_DIR, "**", "*_permalinks.csv"), recursive=True)

sitemaps_generated = []

for csv_path in csv_files:
    filename = os.path.basename(csv_path)
    name = filename.replace("_permalinks.csv", "")  # ej: dubai_lynx2021

    output_file = f"sitemaps/sitemap_{name}.xml"
    out_path = os.path.join(BASE_DIR, output_file)

    df = pd.read_csv(csv_path)

    # Buscar columna 'permalink' ignorando mayúsculas/minúsculas
    cols = {c.lower(): c for c in df.columns}
    if "permalink" not in cols:
        print(f"{filename} no tiene columna 'permalink', se omite")
        continue

    urls = df[cols["permalink"]].apply(
        lambda x: BASE_URL + x if str(x).startswith("/") else str(x)
    ).tolist()

    # Generar XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        xml_content += (
            f"  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <changefreq>monthly</changefreq>\n"
            f"    <priority>0.5</priority>\n"
            f"  </url>\n"
        )

    xml_content += "</urlset>"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    sitemaps_generated.append(BASE_URL + "/" + output_file)

# Ruta al índice
index_path = os.path.join(SITEMAPS_DIR, "sitemap_index.xml")

# Leer los sitemaps existentes si el archivo ya existe
existing_sitemaps = set()
if os.path.exists(index_path):
    tree = ET.parse(index_path)
    root = tree.getroot()
    for sm in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap"):
        loc = sm.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is not None and loc.text:
            existing_sitemaps.add(loc.text.strip())

# Combinar los existentes con los nuevos
all_sitemaps = existing_sitemaps.union(set(sitemaps_generated))

# Escribir el índice actualizado
with open(index_path, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for sm in sorted(all_sitemaps):
        f.write(f"  <sitemap>\n    <loc>{sm}</loc>\n  </sitemap>\n")
    f.write("</sitemapindex>\n")

print("Sitemaps generados y sitemap_index.xml actualizado correctamente.")
