import json
import re
import csv

# =================================
# CONFIG
# =================================
HTML_FILE = "audio_radio.html"   # HTML guardado con view-source
OUTPUT_CSV = "eurobest_2025_audio_radio.csv"

FESTIVAL = "Eurobest"
YEAR = "2025"
TRACK = "Audio - Radio"

AWARD_MAP = {
    "grand_prix": "Grand Prix",
    "gold": "Gold",
    "silver": "Silver",
    "bronze": "Bronze",
    "unawarded": "Shortlist"
}

# =================================
# LOAD HTML
# =================================
with open(HTML_FILE, "r", encoding="utf-8") as f:
    raw = f.read()

# =================================
# EXTRACT CONTENTS ARRAY (CORRECTO)
# =================================
match = re.search(
    r'"contents":\[(.*?)\]\s*,\s*"totalCount"',
    raw,
    re.DOTALL
)

if not match:
    raise Exception("No se encontró el bloque contents[] en el HTML")

contents_raw = match.group(1)

# reconstruir JSON válido
json_text = "[" + contents_raw + "]"
json_text = json_text.replace('\\"', '"')
json_text = json_text.replace('\\n', '')
json_text = json_text.replace('\\t', '')

entries = json.loads(json_text)

print(f"Entries parseadas: {len(entries)}")

# =================================
# PARSE ENTRIES
# =================================
rows = []

for entry in entries:
    try:
        # -----------------------------
        # TITLE
        # -----------------------------
        title = entry.get("title", "").strip()

        # -----------------------------
        # ENRICHMENT DATA
        # -----------------------------
        enrichment = {}
        if entry.get("enrichmentData"):
            enrichment = json.loads(entry["enrichmentData"])

        # -----------------------------
        # BRAND
        # -----------------------------
        brand = ""
        support = enrichment.get("supportText", "")
        if support:
            brand = support.split(",")[0].strip()

        # -----------------------------
        # AGENCY (PRIMERA)
        # -----------------------------
        agency = ""
        contributors = entry.get("contributors", [])
        if contributors:
            agency = contributors[0].get("name", "").strip()

        # -----------------------------
        # CATEGORY
        # -----------------------------
        category = ""
        for tag in entry.get("tags", []):
            if tag.get("level1") == "Lions Award Category":
                category = tag.get("level3", "").strip()
                break

        # -----------------------------
        # AWARD LEVEL
        # -----------------------------
        award_level = "Submitted"
        media = enrichment.get("mediaTag")
        if media and media.get("awardLevel"):
            raw_award = media["awardLevel"].lower()
            award_level = AWARD_MAP.get(raw_award, "Submitted")

        # -----------------------------
        # BOARD IMAGE
        # -----------------------------
        board_image = enrichment.get("imageUrl", "").strip()

        # -----------------------------
        # ROW
        # -----------------------------
        rows.append({
            "Festival": FESTIVAL,
            "Year": YEAR,
            "Track": TRACK,
            "Title": title,
            "Brand": brand,
            "Agency": agency,
            "Category": category,
            "award_level": award_level,
            "board_image": board_image
        })

    except Exception as e:
        print("ERROR parseando entry:", title, "|", e)

# =================================
# WRITE CSV
# =================================
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "Festival",
            "Year",
            "Track",
            "Title",
            "Brand",
            "Agency",
            "Category",
            "award_level",
            "board_image"
        ]
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV generado correctamente: {OUTPUT_CSV}")
