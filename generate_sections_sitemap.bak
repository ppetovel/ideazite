import xml.etree.ElementTree as ET

# Diccionario de festivales y años disponibles
festivals = {
    "canneslions": [2025, 2024, 2023, 2022, 2021, 2020],
    "eurobest":    [2024, 2023, 2022, 2021, 2020],  # (sin 2025)
    "spikes_asia": [2025, 2024, 2023, 2022, 2021],
    "dubai_lynx":  [2025, 2024, 2023, 2022, 2021, 2020],
    "fiap":        [2025],
    "geretyawards":[2025],
    "effie_latam": [2025]
}

base_url = "https://ideazite.com/awards/"

# Crear elementos raíz
urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

# Página Home
url = ET.SubElement(urlset, "url")
ET.SubElement(url, "loc").text = "https://ideazite.com/"
ET.SubElement(url, "changefreq").text = "weekly"
ET.SubElement(url, "priority").text = "1.0"

# Generar URLs para cada festival/año
for fest, years in festivals.items():
    for year in years:
        u = ET.SubElement(urlset, "url")
        ET.SubElement(u, "loc").text = f"{base_url}{fest}/{year}"
        ET.SubElement(u, "changefreq").text = "weekly"
        ET.SubElement(u, "priority").text = "0.8" if fest != "canneslions" else "0.9"

# Guardar el XML
tree = ET.ElementTree(urlset)
tree.write("sitemaps/sitemap_sections.xml", encoding="utf-8", xml_declaration=True)
