# generate_all_sitemaps.py
# Script unico para generar:
# - Sitemaps de campañas desde *_permalinks.csv
# - sitemap_sections.xml detectando awards/<festival>/<year>
# - sitemap_index.xml escaneando sitemaps existentes (con <lastmod>)
# - sitemap.xml raiz que referencia a los dos anteriores
#
# Requisitos:
#   pip install pandas
#
# Notas:
# - Sin emojis y solo ASCII en prints.
# - Normaliza backslashes, espacios, http->https, y asegura URLs absolutas.
# - No asume lista fija de festivales/years: detecta todo lo presente.
# - Orden estable por nombre de archivo para el index.

import os
import re
import glob
import time
import pandas as pd
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, urlunsplit

# ====== CONFIGURACION ======
BASE_URL = "https://ideazite.com"
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
AWARDS_DIR = os.path.join(SITE_ROOT, "awards")
SITEMAPS_DIR = os.path.join(SITE_ROOT, "sitemaps")
os.makedirs(SITEMAPS_DIR, exist_ok=True)

# Prioridad por defecto para sections; Cannes un poco mas alto si se detecta
DEFAULT_SECTION_PRIORITY = "0.8"
CANNES_SECTION_PRIORITY = "0.9"
HOMEPAGE_PRIORITY = "1.0"

# ====== UTILIDADES ======

def _normalize_path_slashes(path: str) -> str:
    # Reemplaza backslashes por forward slashes y colapsa slashes multiples en el path (no en el esquema)
    path = path.replace("\\", "/").strip()
    # Evitar tocar "https://" al colapsar. Trabajamos solo con la parte de path.
    if "://" in path:
        scheme, netloc, p, q, f = urlsplit(path)
        p = re.sub(r"/{2,}", "/", p)
        return urlunsplit((scheme, netloc, p, q, f))
    else:
        return re.sub(r"/{2,}", "/", path)

def _force_https(url: str) -> str:
    return re.sub(r"^http://", "https://", url.strip(), flags=re.IGNORECASE)

def _ensure_absolute(url_or_path: str) -> str:
    """
    Acepta:
      - rutas que comienzan con /awards/...  -> las hace absolutas con BASE_URL
      - URLs absolutas http/https            -> las normaliza y las fuerza a https
    Retorna URL absoluta https.
    """
    s = str(url_or_path or "").strip()
    if not s:
        return ""
    s = _normalize_path_slashes(s)
    # Forzar https si ya es absoluta
    if s.lower().startswith("http://") or s.lower().startswith("https://"):
        return _force_https(s)
    # Si es relativa, asegurar que comience con "/"
    if not s.startswith("/"):
        s = "/" + s
    # Opcional: para consistencia, agregar slash final si no hay query/fragment ni extension
    # y no termina en "/"
    parsed = urlsplit(s)
    if not parsed.query and not parsed.fragment:
        # Heuristica simple: si el path no tiene punto, asumimos "pagina" y agregamos slash
        if not parsed.path.endswith("/") and "." not in os.path.basename(parsed.path):
            s = parsed.path + "/"
        else:
            s = parsed.path
        s = "/" + s.lstrip("/")
    return _force_https(BASE_URL.rstrip("/") + s)

def _iso_date_from_mtime(path: str) -> str:
    try:
        ts = os.path.getmtime(path)
        # Formato ISO8601 simple (YYYY-MM-DD)
        return time.strftime("%Y-%m-%d", time.gmtime(ts))
    except Exception:
        return time.strftime("%Y-%m-%d", time.gmtime())

def _write_xml(tree: ET.ElementTree, out_path: str):
    # Escribe con declaracion XML y UTF-8
    tree.write(out_path, encoding="utf-8", xml_declaration=True)

# ====== 1) SITEMAPS DE CAMPAÑAS DESDE *_permalinks.csv ======

def build_campaign_sitemaps_from_csvs() -> list:
    """
    Busca todos los *_permalinks.csv (excepto *_clean) y genera un sitemap por CSV.
    Devuelve lista de rutas (absolutas web) a los sitemaps generados.
    """
    csv_files = [
        f for f in glob.glob(os.path.join(SITE_ROOT, "**", "*_permalinks.csv"), recursive=True)
        if "_clean" not in os.path.basename(f).lower()
    ]
    generated_urls = []

    for csv_path in csv_files:
        fname = os.path.basename(csv_path)
        name = fname.replace("_permalinks.csv", "")  # ejemplo: fiap2025, dubai_lynx2021, etc.
        out_file = os.path.join(SITEMAPS_DIR, f"sitemap_{name}.xml")

        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"[warn] No se pudo leer {fname}: {e}")
            continue

        # Buscar columna 'permalink' sin case sensitivity
        cols = {c.lower(): c for c in df.columns}
        if "permalink" not in cols:
            print(f"[info] {fname} no tiene columna 'permalink'; se omite.")
            continue

        # Normalizacion de URLs
        urls_raw = df[cols["permalink"]].astype(str).tolist()
        urls_norm = []
        seen = set()
        for u in urls_raw:
            u = u.strip()
            if not u or u.lower() == "nan":
                continue
            u = _normalize_path_slashes(u)
            u = _ensure_absolute(u)
            if not u:
                continue
            # dedupe
            if u not in seen:
                seen.add(u)
                urls_norm.append(u)

        # Construccion del XML
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for u in urls_norm:
            node = ET.SubElement(urlset, "url")
            ET.SubElement(node, "loc").text = u
            ET.SubElement(node, "changefreq").text = "monthly"
            ET.SubElement(node, "priority").text = "0.5"
        _write_xml(ET.ElementTree(urlset), out_file)

        # URL absoluta del sitemap recien generado
        generated_urls.append(_ensure_absolute("/sitemaps/" + os.path.basename(out_file)))

        print(f"[ok] Generado {os.path.basename(out_file)} con {len(urls_norm)} URLs")

    return generated_urls

# ====== 2) SITEMAP SECTIONS DETECTANDO awards/<festival>/<year> ======

def build_sections_sitemap():
    out_file = os.path.join(SITEMAPS_DIR, "sitemap_sections.xml")
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Home
    u = ET.SubElement(urlset, "url")
    ET.SubElement(u, "loc").text = _ensure_absolute("/")
    ET.SubElement(u, "changefreq").text = "weekly"
    ET.SubElement(u, "priority").text = HOMEPAGE_PRIORITY

    # awards/<festival>/<year>
    if os.path.isdir(AWARDS_DIR):
        for fest in sorted(os.listdir(AWARDS_DIR)):
            fest_dir = os.path.join(AWARDS_DIR, fest)
            if not os.path.isdir(fest_dir):
                continue
            # years: carpetas numericas
            for year in sorted(os.listdir(fest_dir)):
                year_dir = os.path.join(fest_dir, year)
                if not os.path.isdir(year_dir):
                    continue
                if not re.fullmatch(r"\d{4}", year):
                    continue
                loc = f"/awards/{fest}/{year}"
                n = ET.SubElement(urlset, "url")
                ET.SubElement(n, "loc").text = _ensure_absolute(loc)
                ET.SubElement(n, "changefreq").text = "weekly"
                # Prioridad un poco mayor para canneslions si existe ese slug
                pr = CANNES_SECTION_PRIORITY if fest.lower() == "canneslions" else DEFAULT_SECTION_PRIORITY
                ET.SubElement(n, "priority").text = pr

    _write_xml(ET.ElementTree(urlset), out_file)
    print(f"[ok] Generado sitemap_sections.xml")

# ====== 3) SITEMAP INDEX a partir de los sitemaps presentes ======

def build_sitemap_index():
    """
    Escanea SITEMAPS_DIR por archivos sitemap_*.xml y arma el index.
    Excluye sitemap_index.xml y sitemap_sections.xml.
    Agrega <lastmod> con mtime del archivo.
    """
    index_path = os.path.join(SITEMAPS_DIR, "sitemap_index.xml")
    files = []
    for fn in os.listdir(SITEMAPS_DIR):
        if not fn.startswith("sitemap_") or not fn.endswith(".xml"):
            continue
        if fn in ("sitemap_index.xml", "sitemap_sections.xml"):
            continue
        files.append(fn)

    # Orden estable por nombre
    files.sort()

    root = ET.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for fn in files:
        sm = ET.SubElement(root, "sitemap")
        loc = _ensure_absolute("/sitemaps/" + fn)
        ET.SubElement(sm, "loc").text = loc
        lastmod = _iso_date_from_mtime(os.path.join(SITEMAPS_DIR, fn))
        ET.SubElement(sm, "lastmod").text = lastmod

    _write_xml(ET.ElementTree(root), index_path)
    print(f"[ok] Actualizado sitemap_index.xml con {len(files)} items")

# ====== 4) SITEMAP RAIZ ======

def build_root_sitemap():
    """
    sitemap.xml raiz con referencias a:
      - /sitemaps/sitemap_index.xml
      - /sitemaps/sitemap_sections.xml
    """
    out_file = os.path.join(SITE_ROOT, "sitemap.xml")
    root = ET.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for fname in ("sitemap_index.xml", "sitemap_sections.xml"):
        sm = ET.SubElement(root, "sitemap")
        ET.SubElement(sm, "loc").text = _ensure_absolute("/sitemaps/" + fname)

    _write_xml(ET.ElementTree(root), out_file)
    print(f"[ok] Regenerado sitemap.xml")

# ====== MAIN ======

def main():
    print("[info] Generando sitemaps de campañas desde *_permalinks.csv ...")
    build_campaign_sitemaps_from_csvs()

    print("[info] Generando sitemap_sections.xml auto-detectando awards/<festival>/<year> ...")
    build_sections_sitemap()

    print("[info] Construyendo sitemap_index.xml a partir de los sitemaps presentes ...")
    build_sitemap_index()

    print("[info] Regenerando sitemap.xml raiz ...")
    build_root_sitemap()

    print("[done] Proceso completado.")

if __name__ == "__main__":
    main()
