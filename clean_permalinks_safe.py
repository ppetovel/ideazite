import pandas as pd
import re
import glob
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def limpiar_texto(texto, stats):
    if pd.isna(texto):
        return texto
    original = str(texto)
    t = original

    # Contadores de problemas
    if "\\" in t:
        stats["backslash"] += 1
    if "“" in t or "”" in t:
        stats["comillas_curvas"] += 1
    if re.search(r"[\u200B-\u200D\uFEFF]", t):
        stats["invisibles"] += 1

    # Reemplazos
    t = t.replace("\\", " ")
    t = t.replace("“", '"').replace("”", '"')
    t = re.sub(r"[\u200B-\u200D\uFEFF]", "", t)

    return t.strip()

# Buscar sólo los CSV *_permalinks.csv
csv_files = glob.glob(os.path.join(BASE_DIR, "awards", "**", "*_permalinks.csv"), recursive=True)

resumen = {}

for archivo_csv in csv_files:
    try:
        df = pd.read_csv(archivo_csv)
        stats = {"backslash": 0, "comillas_curvas": 0, "invisibles": 0}

        for col in df.columns:
            df[col] = df[col].apply(lambda x: limpiar_texto(x, stats))

        # Guardar una copia segura con sufijo _clean.csv
        salida_csv = archivo_csv.replace(".csv", "_clean.csv")
        df.to_csv(salida_csv, index=False, encoding="utf-8")

        resumen[salida_csv] = stats
        print(f"Copia limpia creada: {salida_csv}")
    except Exception as e:
        print(f"No se pudo procesar {archivo_csv}: {e}")

print("\n=== RESUMEN DE PROBLEMAS DETECTADOS ===")
for archivo, stats in resumen.items():
    print(f"{archivo}")
    print(f"  - Backslashes eliminados: {stats['backslash']}")
    print(f"  - Comillas curvas reemplazadas: {stats['comillas_curvas']}")
    print(f"  - Invisibles eliminados: {stats['invisibles']}")
