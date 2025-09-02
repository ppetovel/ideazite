# generate_campaign_pages.py
# Genera páginas de campañas (gris) desde un CSV que YA trae la columna "Permalink".
# Toma el path del Permalink, crea la carpeta local y escribe index.html.
# Salida de consola en ASCII (sin símbolos raros).

import csv, os, argparse, html, pathlib, sys, shutil, urllib.parse

# -------- Config por defecto (ajustables por CLI) --------
FESTIVAL     = "Cannes Lions"
YEAR         = "2020"
SITE_BASE    = "https://ideazite.com"
YEAR_ROOT    = "/awards/canneslions/2020/"
OUTPUT_ROOT  = "./awards/canneslions/2020/campaigns"  # carpeta raíz local donde se crean las subcarpetas de campañas
CONSENT_JS   = "/consent/consent-init.js"
GA_JS        = "/analytics/ga-init.js"
ADS_JS       = "/ads/ads-init.js"

# -------- Utilidades --------
def html_escape(s: str) -> str:
    return html.escape(s or "", quote=True)

def render_board_link(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    return f'<p><a href="{html_escape(url)}" target="_blank" rel="noopener">View Board</a></p>'

def normalize_rel_permalink(p: str) -> str:
    """
    Acepta:
    - Absoluto: https://ideazite.com/awards/... -> devuelve el path "/awards/..."
    - Relativo: awards/... o /awards/... -> asegura leading "/" y trailing "/"
    """
    p = (p or "").strip()
    if not p:
        return ""
    # Si es absoluto, quedarnos con el path
    if p.startswith("http://") or p.startswith("https://"):
        p = urllib.parse.urlsplit(p).path or "/"
    # Asegurar que empiece con "/" y termine con "/"
    if not p.startswith("/"):
        p = "/" + p
    if not p.endswith("/"):
        p = p + "/"
    return p

def slug_from_path(path_with_slashes: str) -> str:
    """
    Devuelve el último segmento no vacío del path como slug.
    Ej: "/awards/canneslions/2020/campaigns/mi-campana/" -> "mi-campana"
    """
    norm = os.path.normpath(path_with_slashes)
    slug = os.path.basename(norm)
    if slug in ("", os.path.sep):
        # fallback si el path termina justo en "/campaigns/"
        parts = [seg for seg in path_with_slashes.split("/") if seg]
        if parts:
            slug = parts[-1]
        else:
            slug = "campaign"
    return slug

# -------- Template de campaña (gris) --------
# Nota: usar %% en CSS para que el operador % del template no choque con porcentajes.
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
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
    "inLanguage": "es",
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

  <!-- Estilos en grises -->
  <style>
    body { font-family: Arial, sans-serif; color:#333; background:#fff; margin:0; }
    a { color:#555; text-decoration:underline; }
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
def generate_pages_from_csv(csv_path: str, clean: bool = False):
    # limpiar carpeta si se pide
    if clean and os.path.isdir(OUTPUT_ROOT):
        shutil.rmtree(OUTPUT_ROOT)
        print("[OK] Carpeta de campañas eliminada antes de generar:", OUTPUT_ROOT)

    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    # Leer CSV original
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    # Verificar que exista la columna "Permalink"
    has_permalink = any(fn.lower().strip() == "permalink" for fn in fieldnames)
    if not has_permalink:
        raise ValueError('El CSV debe incluir la columna "Permalink".')

    # Procesar filas y generar páginas
    for row in rows:
        title       = (row.get("Title") or "").strip()
        brand       = (row.get("Brand") or "").strip()
        agency      = (row.get("Agency") or "").strip()
        track       = (row.get("Track") or "").strip()
        category    = (row.get("Category") or "").strip()
        award_level = (row.get("Award Level") or "").strip()
        board_image = (row.get("Board image") or "").strip()
        year_val    = (row.get("Year") or YEAR).strip() or YEAR

        perm_raw = (row.get("Permalink") or "").strip()
        if not perm_raw:
            print("[WARN] Fila sin Permalink. Saltando. Title:", title)
            continue

        permalink_rel = normalize_rel_permalink(perm_raw)
        if not permalink_rel.startswith("/"):
            # no debería ocurrir, por normalize_rel_permalink, pero por seguridad
            permalink_rel = "/" + permalink_rel

        # Derivar slug desde el permalink
        slug = slug_from_path(permalink_rel)

        # Paths locales
        campaign_dir = os.path.join(OUTPUT_ROOT, slug)
        os.makedirs(campaign_dir, exist_ok=True)

        # URLs
        canonical = f"{SITE_BASE}{permalink_rel}"
        year_url  = f"{SITE_BASE}{YEAR_ROOT}"

        # Render HTML
        data = {
            "TITLE": html_escape(title),
            "TITLE_RAW": html_escape(row.get("Title", "")),
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

        print("[OK] Generado:", out_file)

# -------- CLI --------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera páginas de campañas desde CSV con columna 'Permalink'.")
    parser.add_argument("--csv", required=True, help="Ruta al CSV")
    parser.add_argument("--site-base", default=SITE_BASE)
    parser.add_argument("--year-root", default=YEAR_ROOT)
    parser.add_argument("--outdir", default=OUTPUT_ROOT)
    parser.add_argument("--festival", default=FESTIVAL)
    parser.add_argument("--year", default=YEAR)
    parser.add_argument("--clean", action="store_true", help="Borra la carpeta de campañas antes de generar")
    args = parser.parse_args()

    SITE_BASE = args.site_base.rstrip("/")
    YEAR_ROOT = args.year_root if args.year_root.endswith("/") else args.year_root + "/"
    OUTPUT_ROOT = args.outdir
    FESTIVAL = args.festival
    YEAR = args.year

    try:
        generate_pages_from_csv(args.csv, clean=args.clean)
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
