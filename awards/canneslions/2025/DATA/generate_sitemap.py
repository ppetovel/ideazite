import pandas as pd
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree

# Configuración
festival = "canneslions"
year = "2025"
base_url = f"https://ideazite.com/awards/{festival}/{year}"
csv_path = Path("cannes2025_permalinks.csv")  # CSV con columna 'Permalink'
output_path = Path(f"sitemap-{festival}-{year}.xml")

# Leer CSV
df = pd.read_csv(csv_path)
urls = df['Permalink'].dropna().unique()

# Crear sitemap XML
urlset = Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

# URL índice del festival/año
url = SubElement(urlset, 'url')
SubElement(url, 'loc').text = base_url
SubElement(url, 'changefreq').text = 'weekly'
SubElement(url, 'priority').text = '0.9'

# URLs de campañas
for u in urls:
    # Asegurar que la URL sea absoluta
    if not u.startswith("http"):
        u = "https://ideazite.com" + u
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = u
    SubElement(url, 'changefreq').text = 'monthly'
    SubElement(url, 'priority').text = '0.5'

# Guardar el archivo XML
ElementTree(urlset).write(output_path, encoding='utf-8', xml_declaration=True)

print(f"Sitemap generado: {output_path}")
