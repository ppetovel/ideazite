import re
import sys
from pathlib import Path

# Uso:
# python add_festival.py "Nombre Festival" slug clase [color_base] [color_hover] año
# Si el festival ya existe, los colores se ignoran y podés omitirlos:
# python add_festival.py "Cannes Lions" cannes cannes 2026

if len(sys.argv) < 5:
    print("")
    print("Uso correcto:")
    print('python add_festival.py "Nombre Festival" slug clase [color_base] [color_hover] año')
    print('Ejemplo (nuevo festival): python add_festival.py "Effie Argentina" effie_argentina effiear "#2a6fb3" "#3a88d1" 2026')
    print('Ejemplo (festival ya existente): python add_festival.py "Cannes Lions" cannes cannes 2026')
    sys.exit(1)

festival_name = sys.argv[1]
festival_slug = sys.argv[2]
festival_class = sys.argv[3]

# Si el usuario pasa 6 argumentos, es nuevo festival (tiene color y hover)
if len(sys.argv) == 7:
    festival_color = sys.argv[4]
    festival_hover = sys.argv[5]
    year = sys.argv[6]
elif len(sys.argv) == 5:
    # caso sin color, festival ya existente
    festival_color = None
    festival_hover = None
    year = sys.argv[4]
else:
    print("Cantidad de argumentos incorrecta.")
    sys.exit(1)

html_file = Path("index.html")
if not html_file.exists():
    print("No se encontró index.html en esta carpeta.")
    sys.exit(1)

html = html_file.read_text(encoding="utf-8")

# 1. Detectar si el festival ya existe en cualquier año
existing_class_pattern = rf'class="button {festival_class}"'
festival_exists = re.search(existing_class_pattern, html) is not None

# 2. Detectar todos los años existentes
years = re.findall(r'<section class="year" aria-label="Festivales (\d{4})">', html)
years = [int(y) for y in years]
min_year, max_year = (min(years), max(years)) if years else (None, None)
target_year = int(year)

# 3. Crear el botón del festival
new_button = f'        <a href="/awards/{festival_slug}/{year}/" class="button {festival_class}">{festival_name} {year}</a>\n'

# 4. Si el año ya existe, insertar dentro del bloque
year_pattern = re.compile(
    rf'(<section class="year" aria-label="Festivales {year}">.*?<div class="grid">)(.*?)(</div>)', re.S
)
if year_pattern.search(html):
    print(f"Año {year} encontrado. Agregando festival dentro de la sección existente...")
    html = re.sub(year_pattern, lambda m: m.group(1) + m.group(2) + new_button + m.group(3), html)

# 5. Si el año no existe, crear una nueva sección
else:
    print(f"Año {year} no encontrado. Creando nueva sección...")
    new_section = f"""
    <!-- {year} -->
    <section class="year" aria-label="Festivales {year}">
      <h2>Festivales {year}</h2>
      <div class="grid">
{new_button.strip()}
      </div>
    </section>
"""
    if years:
        if target_year > max_year:
            print(f"Colocando {year} al inicio (más reciente).")
            html = re.sub(r"(<!-- \d{4} -->)", new_section + r"\n\1", html, count=1)
        elif target_year < min_year:
            print(f"Colocando {year} al final (más antiguo).")
            html = re.sub(r"(</section>\s*</main>)", r"</section>\n" + new_section + r"\n\1", html, count=1)
        else:
            inserted = False
            for y in sorted(years):
                if target_year > y:
                    continue
                html = re.sub(rf"(<!-- {y} -->)", new_section + r"\n\1", html, count=1)
                inserted = True
                break
            if not inserted:
                html = html.replace("</main>", new_section + "\n</main>")
    else:
        html = html.replace("</main>", new_section + "\n</main>")

# 6. Si el festival no existía antes, crear su clase y variable CSS
if not festival_exists:
    if festival_color is None or festival_hover is None:
        print("Error: se necesita color base y hover para crear un festival nuevo.")
        sys.exit(1)
    print(f"Festival nuevo detectado. Agregando clase CSS y color base...")

    html = re.sub(
        r"(--loerie:[^;]+;)",
        r"\1\n      " + f"--{festival_class}:{festival_color}; /* {festival_name} */",
        html,
        count=1
    )

    css_rule = f"""
    .{festival_class}{{ background: var(--{festival_class}); border-color: var(--{festival_class}); }}
    .{festival_class}:hover{{ background: {festival_hover}; border-color: {festival_hover}; }}
"""
    html = re.sub(r"(\.loerie:hover\{[^\}]+\})", r"\1" + css_rule, html, count=1)

else:
    print(f"Festival '{festival_name}' ya existente, respetando su color original.")

# 7. Guardar cambios
html_file.write_text(html, encoding="utf-8")
print(f"Festival '{festival_name} {year}' agregado correctamente en {html_file.name}.")
