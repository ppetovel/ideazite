import io

# Ruta del CSV específico
path = "./awards/effie_latam/2025/data/effie_latam2025.csv"

# Leer el contenido actual (UTF-8 sin BOM, con caracteres rotos visibles)
with open(path, "r", encoding="utf-8", errors="replace") as fr:
    content = fr.read()

# Guardar con UTF-8 con BOM (utf-8-sig)
with open(path, "w", encoding="utf-8-sig", newline="") as fw:
    fw.write(content)

print("[OK] Archivo convertido a UTF-8 con BOM:", path)
