# generate_index.py
# Genera el index.html de un festival usando un template con placeholders {{...}}

import os, argparse

def main():
    parser = argparse.ArgumentParser(description="Generar index de festival desde template")
    parser.add_argument("--festival", required=True, help="Nombre del festival (ej: LIA Awards)")
    parser.add_argument("--slug", required=True, help="Slug (ej: lia_awards)")
    parser.add_argument("--year", required=True, help="Año (ej: 2025)")
    parser.add_argument("--desc", required=True, help="Descripción corta SOLO para meta description")
    parser.add_argument("--template", default="./templates/index_template.html", help="Ruta al template base")
    args = parser.parse_args()

    # Texto fijo para la intro en el body
    intro_text = (
        f"Esta base de datos reúne inscripciones con detalles de track, título, "
        f"brand, agency, award e imagen. Explora campañas destacadas en {args.festival} {args.year}. "
        f"Al final de la tabla, el CSV del festival completo."
    )

    # Leer el template
    with open(args.template, "r", encoding="utf-8") as f:
        html = f.read()

    # Reemplazar placeholders
    html = (html
        .replace("{{FESTIVAL_NAME}}", args.festival)
        .replace("{{YEAR}}", str(args.year))
        .replace("{{SLUG}}", args.slug)
        .replace("{{DESCRIPTION}}", args.desc)  # solo para meta description
        .replace("{{INTRO}}", intro_text)       # nuevo: intro automático
        .replace("{{COLUMNS}}", "Track,Title,Brand,Agency,Award")
        .replace("{{LINK_COLUMN}}", "Title")
    )

    # Ruta de salida
    outdir = f"./awards/{args.slug}/{args.year}/"
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, "index.html")

    # Escribir archivo
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(html)

    print("[OK] index generado:", outfile)

if __name__ == "__main__":
    main()
