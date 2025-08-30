# generate_campaign_pages.py
# Genera páginas de campañas (gris) desde CSV con slug: Title + Brand + Agency + Year
# y crea un CSV nuevo con columna "Permalink" (ruta relativa).
# Salida de consola en ASCII (sin símbolos raros).

import csv, os, re, unicodedata, argparse, html, pathlib, sys, shutil

# -------- Config por defecto para Cannes 2020 --------
FESTIVAL     = "Cannes Lions"
YEAR         = "2020"
SITE_BASE    = "https://ideazite.com"
YEAR_ROOT    = "/awards/canneslions/2020/"
OUTPUT_ROOT  = "./awards/canneslions/2020/campaigns"  # carpeta de salida
CONSENT_JS   = "/consent/consent-init.js"
GA_JS        = "/analytics/ga-init.js"
ADS_JS       = "/ads/ads-init.js"

# -------- Utilidades --------
def slugify(text: str) -> str:
    text = (text or "").strip()
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = text.lower().replace('&', ' and ')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text).strip('-')
    return text

def html_escape(s: str) -> str:
    return html.escape(s or "", quote=True)

def ensure_unique(slug: str, used: set) -> str:
    base = slug
    i = 2
    while slug in used:
        slug = f"{base}-{i}"
        i += 1
    used.add(slug)
    return slug

def render_board_link(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    return f'<p><a href="{html_escape(url)}" target="_blank" rel="noopener">View Board</a></p>'

# -------- Template de campaña (gris, igual al ejemplo que pasaste) --------
# Nota: para que el operador % no choque con porcentajes en CSS, usar %%.
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">

  <title>%(TITLE)s - %(BRAND)s | %(FESTIVAL)s %(YEAR)s</title>
  <meta name="description" content="%(TITLE)s for %(BRAND)s, created by %(AGENCY)s. Track: %(TRACK)s. Award: %(AWARD_LEVEL)s. %(FESTIVAL)s %(YEAR)s.">
  <link rel="canonical" href="%(CANONICAL)s">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="keywords" content="%(FESTIVAL)s %(YEAR)s, %(TITLE)s, %(BRAND)s, %(AGENCY)s, %(TRACK)s, %(CATEGORY)s, %(AWARD_LEVEL)s, advertising campaign">

  <!-- Open Graph -->
  <meta property="og:title" content="%(TITLE)s - %(BRAND)s | %(FESTIVAL)s %(YEAR)s">
  <meta property="og:description" content="Created by %(AGENCY)s. Track: %(TRACK)s. Award: %(AWARD_LEVEL)s.">
  <meta property="og:type" content="article">
  <meta property="og:url" content="%(CANONICAL)s">
  <meta property="og:image" content="%(BOARD_IMAGE)s">
  <meta property="og:image:alt" content="Board image of %(TITLE)s">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="%(TITLE)s - %(BRAND)s | %(FESTIVAL)s %(YEAR)s">
  <meta name="twitter:description" content="%(AGENCY)s. %(TRACK)s. %(AWARD_LEVEL)s.">
  <meta name="twitter:image" content="%(BOARD_IMAGE)s">
  <meta name="twitter:image:alt" content="Board image of %(TITLE)s">

  <!-- JSON-LD -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "CreativeWork",
    "name": "%(TITLE)s",
    "url": "%(CANONICAL)s",
    "inLanguage": "en",
    "isPartOf": { "@type": "CreativeWorkSeries", "name": "%(FESTIVAL)s %(YEAR)s", "url": "%(YEAR_URL)s" },
    "about": "%(FESTIVAL)s",
    "temporalCoverage": "%(YEAR)s",
    "brand": { "@type": "Brand", "name": "%(BRAND)s" },
    "creator": { "@type": "Organization", "name": "%(AGENCY)s" },
    "genre": ["%(TRACK)s", "%(CATEGORY)s"],
    "award": "%(AWARD_LEVEL)s",
    "image": "%(BOARD_IMAGE)s"
  }
  </script>

  <link rel="icon" type="image/x-icon" href="/icons/favicon.ico">

  <!-- Centralizado -->
  <script src="%(CONSENT_JS)s" defer></script>
  <script src="%(GA_JS)s" defer></script>
  <script src="%(ADS_JS)s" defer></script>

  <!-- Estilos en grises (tal cual tu ejemplo) -->
  <style>
    body { font-family: Arial, sans-serif; color:#333; background:#fff; margin:0; }
    a { color:#555; text-decoration:none; }
    a:hover { text-decoration:underline; color:#000; }
    .wrap { max-width: 800px; margin: 0 auto; padding: 16px; }
    h1 { color:#444; margin-bottom: 8px; }
    table { border-collapse: collapse; width: 100%%; margin-top: 14px; }
    th, td { border:1px solid #ccc; padding:6px 8px; text-align:left; font-size:14px; vertical-align:top; }
    th { width: 180px; background:#f7f7f7; color:#555; font-weight:normal; }
    .links { margin: 18px 0; }

    /* Ads placeholders (2 slots) */
    .ad-slot { margin: 16px 0; }
    .ad-top, .ad-footer { min-height: 90px; border:1px dashed #ccc; background:#f7f7f7; }
    .ad-fallback { font: 12px/1.4 Arial, sans-serif; color:#666; text-align:center; padding:12px; }
    @media (max-width:600px){ .ad-top, .ad-footer { min-height: 60px; } }

    /* Footer styles (aplican al include) */
    .site-footer { margin:28px auto 22px; padding:14px 16px; max-width:920px; border-top:1px solid #ccc; color:#555; font-size:14px; line-height:1.4; }
    .site-footer .social { margin-top:8px; }
    .site-footer .social a { display:inline-block; margin-right:14px; text-decoration:none; color:#555; border-bottom:1px dotted #777; }
    .site-footer .social a:hover { color:#000; border-bottom-color:#000; }
    @media (max-width:600px){ .site-footer{ padding:16px; font-size:15px; } .site-footer .social a{ margin-right:12px; } }
  </style>
</head>
<body>
  <div class="wrap">
    <nav><a href="%(YEAR_URL)s">← Back to %(FESTIVAL)s %(YEAR)s</a></nav>

    <!-- AD top -->
    <div class="ad-slot ad-top" data-ad-slot="top">
      <div class="ad-fallback">Advertisement</div>
    </div>

    <h1>%(TITLE)s</h1>
    <p><em>%(FESTIVAL)s %(YEAR)s · %(TRACK)s</em></p>

    <table>
      <tr><th>Festival</th><td>%(FESTIVAL)s</td></tr>
      <tr><th>Year</th><td>%(YEAR)s</td></tr>
      <tr><th>Track</th><td>%(TRACK)s</td></tr>
      <tr><th>Title</th><td>%(TITLE_RAW)s</td></tr>
      <tr><th>Brand</th><td>%(BRAND)s</td></tr>
      <tr><th>Agency</th><td>%(AGENCY)s</td></tr>
      <tr><th>Category</th><td>%(CATEGORY)s</td></tr>
      <tr><th>Award Level</th><td>%(AWARD_LEVEL)s</td></tr>
    </table>

    <div class="links">
      %(BOARD_LINK)s
      <!-- Si algun dia hay video:
      <p><a href="%(CASE_VIDEO)s" target="_blank" rel="noopener">Case video</a></p>
      -->
    </div>

    <!-- AD bottom -->
    <div class="ad-slot ad-footer" data-ad-slot="footer">
      <div class="ad-fallback">Advertisement</div>
    </div>
  </div>

  <!-- Footer include -->
  <div id="footer-container"></div>
  <script>
    (function(){
      fetch("/includes/footer.html")
        .then(function(r){ return r.text(); })
        .then(function(html){ document.getElementById("footer-container").innerHTML = html; })
        .catch(function(){});
    })();
  </script>
</body>
</html>
"""

# -------- Generador --------
def generate_pages_and_permalink_csv(csv_path: str, permalink_csv_out: str, clean: bool = False):
    # limpiar carpeta si se pide
    if clean and os.path.isdir(OUTPUT_ROOT):
        shutil.rmtree(OUTPUT_ROOT)
        print("[OK] Carpeta de campañas eliminada antes de generar:", OUTPUT_ROOT)

    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    used_slugs = set()

    # Leer CSV original
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    # Asegurar columna Permalink al final si no existe
    has_permalink = any(fn.lower().strip() == "permalink" for fn in fieldnames)
    if not has_permalink:
        fieldnames_out = fieldnames + ["Permalink"]
    else:
        fieldnames_out = fieldnames[:]  # mismo orden

    # Procesar filas y generar páginas
    out_rows = []
    for row in rows:
        title       = (row.get("Title") or "").strip()
        brand       = (row.get("Brand") or "").strip()
        agency      = (row.get("Agency") or "").strip()
        track       = (row.get("Track") or "").strip()
        category    = (row.get("Category") or "").strip()
        award_level = (row.get("Award Level") or "").strip()
        board_image = (row.get("Board image") or "").strip()
        year_val    = (row.get("Year") or YEAR).strip() or YEAR

        # SLUG
        slug_seed = " ".join([title, brand, agency, year_val])
        slug = slugify(slug_seed)
        slug = ensure_unique(slug, used_slugs)

        # Paths
        campaign_dir = os.path.join(OUTPUT_ROOT, slug)
        os.makedirs(campaign_dir, exist_ok=True)

        canonical = f"{SITE_BASE}{YEAR_ROOT}campaigns/{slug}/"
        year_url  = f"{SITE_BASE}{YEAR_ROOT}"
        permalink_rel = f"{YEAR_ROOT}campaigns/{slug}/"

        # Render HTML
        data = {
            "TITLE": html_escape(title),
            "TITLE_RAW": html_escape(row.get("Title","")),
            "BRAND": html_escape(brand),
            "AGENCY": html_escape(agency),
            "TRACK": html_escape(track),
            "CATEGORY": html_escape(category),
            "AWARD_LEVEL": html_escape(award_level),
            "FESTIVAL": html_escape(FESTIVAL),
            "YEAR": html_escape(year_val),
            "BOARD_IMAGE": html_escape(board_image),
            "BOARD_LINK": render_board_link(board_image),

            "CANONICAL": canonical,
            "YEAR_URL": year_url,

            "CONSENT_JS": CONSENT_JS,
            "GA_JS": GA_JS,
            "ADS_JS": ADS_JS,

            "CASE_VIDEO": ""
        }

        html_out = PAGE_TEMPLATE % data

        # Escribir index.html
        out_file = os.path.join(campaign_dir, "index.html")
        with open(out_file, "w", encoding="utf-8") as wf:
            wf.write(html_out)

        # Fila de salida con Permalink
        new_row = {k: row.get(k, "") for k in fieldnames}
        if has_permalink:
            if not (new_row.get("Permalink") or "").strip():
                new_row["Permalink"] = permalink_rel
        else:
            new_row["Permalink"] = permalink_rel

        out_rows.append(new_row)
        print("[OK] Generado:", out_file)

    # Escribir CSV de salida con Permalink
    with open(permalink_csv_out, "w", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=fieldnames_out)
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)

    print("[OK] CSV con Permalink creado:", permalink_csv_out)

# -------- CLI --------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera páginas de campañas desde CSV y crea CSV con Permalink.")
    parser.add_argument("--csv", required=True, help="Ruta al CSV")
    parser.add_argument("--site-base", default=SITE_BASE)
    parser.add_argument("--year-root", default=YEAR_ROOT)
    parser.add_argument("--outdir", default=OUTPUT_ROOT)
    parser.add_argument("--festival", default=FESTIVAL)
    parser.add_argument("--year", default=YEAR)
    parser.add_argument("--permalink-csv-out", default=None)
    parser.add_argument("--clean", action="store_true", help="Borra la carpeta de campañas antes de generar")
    args = parser.parse_args()

    SITE_BASE = args.site_base.rstrip("/")
    YEAR_ROOT = args.year_root if args.year_root.endswith("/") else args.year_root + "/"
    OUTPUT_ROOT = args.outdir
    FESTIVAL = args.festival
    YEAR = args.year

    if args.permalink_csv_out:
        permalink_csv_out = args.permalink_csv_out
    else:
        in_path = pathlib.Path(args.csv)
        permalink_csv_out = str(in_path.with_name(in_path.stem + "_permalinks" + in_path.suffix))

    try:
        generate_pages_and_permalink_csv(args.csv, permalink_csv_out, clean=args.clean)
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
