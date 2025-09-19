import pandas as pd
import os

# Carpeta actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base de URL de tu sitio
BASE_URL = "https://ideazite.com"

# Lista de CSV a procesar
CSV_FILES = [
    ("cannes2025_permalinks.csv", "sitemaps/sitemap_cannes2025.xml"),
    ("spikes_asia2025_permalinks.csv", "sitemaps/sitemap_spikes_asia2025.xml"),
    ("dubai_lynx2025_permalinks.csv", "sitemaps/sitemap_dubai_lynx2025.xml"),
    ("fiap2025_permalinks.csv", "sitemaps/sitemap_fiap2025.xml"),
    ("geretyawards2025_permalinks.csv", "sitemaps/sitemap_geretyawards2025.xml"),
    ("effie_latam2025_permalinks.csv", "sitemaps/sitemap_effie_latam2025.xml")
]

# Crear carpeta sitemaps si no existe
sitemaps_dir = os.path.join(BASE_DIR, "sitemaps")
os.makedirs(sitemaps_dir, exist_ok=True)

# Crear cada sitemap individual
sitemaps_generated = []

for csv_file, output_file in CSV_FILES:
    csv_path = os.path.join(BASE_DIR, csv_file)

    if not os.path.exists(csv_path):
        print(f"{csv_file} no existe, se omite")
        continue

    df = pd.read_csv(csv_path)

    # Buscar la columna 'permalink' ignorando mayúsculas/minúsculas
    cols = {c.lower(): c for c in df.columns}
    if 'permalink' not in cols:
        print(f"{csv_file} no tiene columna 'permalink', se omite")
        continue

    urls = df[cols['permalink']].apply(lambda x: BASE_URL + x if str(x).startswith('/') else str(x)).tolist()

    # Generar contenido XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        xml_content += f'  <url>\n    <loc>{url}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>\n'

    xml_content += '</urlset>'

    # Guardar sitemap
    out_path = os.path.join(BASE_DIR, output_file)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    sitemaps_generated.append(BASE_URL + '/' + output_file)

# Generar el sitemap índice
index_path = os.path.join(BASE_DIR, "sitemaps", "sitemap_index.xml")
with open(index_path, 'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for sm in sitemaps_generated:
        f.write(f'  <sitemap>\n    <loc>{sm}</loc>\n  </sitemap>\n')
    f.write('</sitemapindex>')

print("Sitemaps generados correctamente.")
