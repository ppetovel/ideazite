# generate_campaign_pages_lia2025.py
# Genera páginas de campañas (gris) desde CSV con slug: Title + Brand + Agency + Year
# y crea un CSV nuevo con columna "Permalink" (ruta web relativa).
# Salida de consola en ASCII (sin símbolos raros).

import csv, os, re, unicodedata, argparse, html, pathlib, sys, shutil, urllib.parse

# -------- Config por defecto --------
FESTIVAL     = "London International Awards - LIA"
YEAR         = "2025"
SITE_BASE    = "https://ideazite.com"
YEAR_ROOT    = "/awards/lia_awards/2025/"
OUTPUT_ROOT  = "./awards/lia_awards/2025/campaigns"
CONSENT_JS   = "/consent/consent-init.js"
GA_JS        = "/analytics/ga-init.js"
ADS_JS       = "/ads/ads-init.js"

MAX_SLUG_LEN = 120

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
    base = slug[:MAX_SLUG_LEN].rstrip('-')
    slug = base
    i = 2
    while slug in used:
        room = max(1, MAX_SLUG_LEN - (len(str(i)) + 1))
        slug = (base[:room].rstrip('-')) + f"-{i}"
        i += 1
    used.add(slug)
    return slug

def render_board_link(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    return f'<p><a href="{html_escape(url)}" target="_blank" rel="noopener">View Board</a></p>'

def ensure_dir_for_file(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)

# -------- Template de campaña --------
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">

  <title>%(TITLE)s - %(BRAND)s | %(FESTIVAL)s %(YEAR)s</title>
  <meta name="description" content="%(TITLE)s for %(BRAND)s, created by %(AGENCY)s. Award: %(AWARD)s. %(FESTIVAL)s %(YEAR)s.">
  <link rel="canonical" href="%(CANONICAL)s">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Open Graph -->
  <meta property="og:title" content="%(TITLE)s - %(BRAND)s | %(FESTIVAL)s %(YEAR)s">
  <meta property="og:description" content="Created by %(AGENCY)s. Award: %(AWARD)s.">
  <meta property="og:type" content="article">
  <meta property="og:url" content="%(CANONICAL)s">
  <meta property="og:image" content="%(BOARD_IMAGE)s">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="%(TITLE)s - %(BRAND)s | %(FESTIVAL)s %(YEAR)s">
  <meta name="twitter:description" content="%(AGENCY)s. Award: %(AWARD)s.">
  <meta name="twitter:image" content="%(BOARD_IMAGE)s">

  <link rel="icon" type="image/x-icon" href="/icons/favicon.ico">

  <!-- Centralizado -->
  <script src="%(CONSENT_JS)s" defer></script>
  <script src="%(GA_JS)s" defer></script>
  <script src="%(ADS_JS)s" defer></script>

  <style>
    body { font-family: Arial, sans-serif; color:#333; background:#fff; margin:0; }
    a { color:#555; text-decoration:underline; }
    a:hover { text-decoration:underline; color:#000; }
    .wrap { max-width: 800px; margin: 0 auto; padding: 16px; }
    h1 { color:#444; margin-bottom: 8px; }
    table { border-collapse: collapse; width: 100%%; margin-top: 14px; }
    th, td { border:1px solid #ccc; padding:6px 8px; text-align:left; font-size:14px; vertical-align:top; }
    th { width: 200px; background:#f7f7f7; color:#555; font-weight:normal; }
    .links { margin: 18px 0; }
    .ad-slot { margin: 16px 0; }
    .ad-top, .ad-footer { min-height: 90px; border:1px dashed #ccc; background:#f7f7f7; }
    .ad-fallback { font: 12px/1.4 Arial, sans-serif; color:#666; text-align:center; padding:12px; }
    @media (max-width:600px){ .ad-top, .ad-footer { min-height: 60px; } }
    .site-footer { margin:28px auto 22px; padding:14px 16px; max-width:920px; border-top:1px solid #ccc; color:#555; font-size:14px; line-height:1.4; }
  </style>
</head>
<body>
  <div class="wrap">
    <nav><a href="%(YEAR_URL)s">← Back to %(FESTIVAL)s %(YEAR)s</a></nav>

    <div class="ad-slot ad-top"><div class="ad-fallback">Advertisement</div></div>

    <h1>%(TITLE)s</h1>
    <p><em>%(FESTIVAL)s %(YEAR)s</em></p>

    <table>
%(TABLE_ROWS)s
    </table>

    <div class="links">
      %(BOARD_LINK)s
    </div>

    <div class="ad-slot ad-footer"><div class="ad-fallback">Advertisement</div></div>
  </div>

  <div id="footer-container"></div>
  <script>
    fetch("/includes/footer.html")
      .then(r=>r.text())
      .then(html=>{ document.getElementById("footer-container").innerHTML=html; })
      .catch(()=>{});
  </script>
</body>
</html>
"""

# -------- Generador --------
def generate_pages_and_permalink_csv(csv_path: str, permalink_csv_out: str, clean: bool = False):
    if clean and os.path.isdir(OUTPUT_ROOT):
        shutil.rmtree(OUTPUT_ROOT)
        print("[OK] Campaign folder removed before generate:", OUTPUT_ROOT)

    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    used_slugs = set()

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    has_permalink = any((fn or "").lower().strip() == "permalink" for fn in fieldnames)
    fieldnames_out = (fieldnames + ["Permalink"]) if not has_permalink else fieldnames[:]

    out_rows = []
    failed = 0

    for idx, row in enumerate(rows, 1):
        try:
            title       = (row.get("Title") or "").strip()
            brand       = (row.get("Brand") or "").strip()
            agency      = (row.get("Agency") or "").strip()
            year_val    = (row.get("Year") or YEAR).strip() or YEAR

            slug_seed = " ".join([title, brand, agency, year_val])
            slug = ensure_unique(slugify(slug_seed), used_slugs)

            campaign_dir = os.path.join(OUTPUT_ROOT, slug)
            os.makedirs(campaign_dir, exist_ok=True)

            canonical = f"{SITE_BASE}{YEAR_ROOT}campaigns/{slug}/"
            year_url  = f"{SITE_BASE}{YEAR_ROOT}"
            permalink_rel = f"{YEAR_ROOT}campaigns/{slug}/"   # <-- SIEMPRE URL WEB

            # Construir filas de tabla con todas las columnas del CSV
            table_rows = ""
            for col in fieldnames:
                if col.lower().strip() == "permalink":
                    continue
                val = row.get(col, "")
                table_rows += f"      <tr><th>{html_escape(col)}</th><td>{html_escape(val)}</td></tr>\n"

            data = {
                "TITLE": html_escape(title),
                "BRAND": html_escape(brand),
                "AGENCY": html_escape(agency),
                "AWARD": html_escape(row.get("Award","")),
                "FESTIVAL": html_escape(FESTIVAL),
                "YEAR": html_escape(year_val),
                "BOARD_IMAGE": html_escape(row.get("Board image","")),
                "BOARD_LINK": render_board_link(row.get("Board image","")),
                "CANONICAL": canonical,
                "YEAR_URL": year_url,
                "CONSENT_JS": CONSENT_JS,
                "GA_JS": GA_JS,
                "ADS_JS": ADS_JS,
                "TABLE_ROWS": table_rows
            }

            html_out = PAGE_TEMPLATE % data
            out_file = os.path.join(campaign_dir, "index.html")
            with open(out_file, "w", encoding="utf-8") as wf:
                wf.write(html_out)

            new_row = {k: row.get(k, "") for k in fieldnames}
            if has_permalink:
                if not (new_row.get("Permalink") or "").strip():
                    new_row["Permalink"] = permalink_rel
            else:
                new_row["Permalink"] = permalink_rel

            out_rows.append(new_row)
            print("[OK] Generated:", out_file)

        except Exception as e:
            failed += 1
            print(f"[WARN] Campaign {idx} failed: {e}")
            continue

    ensure_dir_for_file(permalink_csv_out)
    with open(permalink_csv_out, "w", newline="", encoding="utf-8") as wf:
        writer = csv.DictWriter(wf, fieldnames=fieldnames_out)
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)

    print("[OK] Permalink CSV created:", permalink_csv_out)
    if failed:
        print(f"[INFO] Failed campaigns: {failed}")

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
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    SITE_BASE = args.site_base.rstrip("/")

    def _to_web_root(s: str) -> str:
        s = (s or "").strip().replace("\\", "/")
        if s.startswith("http://") or s.startswith("https://"):
            s = urllib.parse.urlsplit(s).path or "/"
        m = re.search(r"(/awards/.*)$", s, flags=re.IGNORECASE)
        if m:
            s = m.group(1)
        if not s.startswith("/"):
            s = "/" + s
        if not s.endswith("/"):
            s = s + "/"
        return s

    YEAR_ROOT = _to_web_root(args.year_root)
    OUTPUT_ROOT = args.outdir
    FESTIVAL = args.festival
    YEAR = str(args.year)

    if args.permalink_csv_out:
        permalink_csv_out = args.permalink_csv_out
    else:
        in_path = pathlib.Path(args.csv)
        base_name = in_path.stem + "_permalinks" + in_path.suffix
        year_root_local = "." + YEAR_ROOT
        data_dir = os.path.join(year_root_local, "data")
        permalink_csv_out = os.path.join(data_dir, base_name)

    try:
        generate_pages_and_permalink_csv(args.csv, permalink_csv_out, clean=args.clean)
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
