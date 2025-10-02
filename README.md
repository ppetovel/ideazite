Perfecto 👌, te armo un **README.md** listo para guardar en la raíz del repo (`ideazite/README.md`).
Ahí tenés explicado cómo usar cada script y ejemplos con diferentes festivales.

---

## `README.md`

```markdown
# Ideazite – Generación automática de festivales

Este proyecto permite generar automáticamente todas las páginas de campañas e índices de cada festival a partir de un CSV limpio.

---

## Flujo completo

1. Colocar el CSV limpio en la carpeta del festival:
```

/awards/[slug]/[year]/data/[slug][year].csv

```

Ejemplo:
```

/awards/test_awards/2025/data/test_awards2025.csv

````

2. Ejecutar el script maestro `generate_festival.sh` desde la raíz del proyecto:
```bash
./generate_festival.sh "Nombre Festival" slug year "descripcion" "cols" linkcol
````

### Parámetros

* `"Nombre Festival"` → Nombre completo del festival (ej: `"Cannes Lions"`).
* `slug` → Identificador usado en carpetas y URLs (ej: `canneslions`, `spikes_asia`).
* `year` → Año del festival (ej: `2025`).
* `"descripcion"` → Texto corto que aparecerá en el index (ej: `"el festival de creatividad más importante del mundo"`).
* `"cols"` → Columnas a mostrar en la tabla del index, separadas por coma.
  *(si se deja vacío `""`, se muestran todas)*.
* `linkcol` → Nombre de la columna que será link a la campaña (normalmente `Title`).

3. Ver el resultado levantando un servidor local:

   ```bash
   python -m http.server 8000
   ```

   Y abrir en el navegador:

   ```
   http://localhost:8000/awards/[slug]/[year]/index.html
   ```

---

## Ejemplos de uso

### Test Awards 2025

```bash
./generate_festival.sh "Test Awards" test_awards 2025 "un festival de prueba" "Title,Brand,Agency,Award" Title
```

### Cannes Lions 2025

```bash
./generate_festival.sh "Cannes Lions" canneslions 2025 "el festival de creatividad más importante del mundo" "Title,Brand,Agency,Award,Country,Track" Title
```

### Spikes Asia 2024

```bash
./generate_festival.sh "Spikes Asia" spikes_asia 2024 "el festival de creatividad de Asia-Pacífico" "Title,Brand,Agency,Award,Country" Title
```

### Effie Latin America 2025

```bash
./generate_festival.sh "Effie Awards Latin America" effie_latam 2025 "el gran festival de la efectividad en la región" "Title,Brand,Agency,Award,Category" Title
```

---

## Scripts disponibles

* **`generate_campaigns.sh`**
  Genera las páginas de campañas y el CSV con permalinks.

* **`generate_index.sh`**
  Genera el index del festival a partir del `_permalinks.csv`.

* **`generate_festival.sh`**
  Ejecuta ambos pasos (campañas + index) en un solo comando.

* **`run_local.sh`**
  Levanta un servidor local en `http://localhost:8000`.

---

## Notas

* Todas las páginas individuales de campaña incluyen **todas las columnas del CSV**.
* El index muestra solo las columnas definidas en `--columns`.
* La columna indicada en `--link-column` se convierte en link hacia la página de campaña.

```

---

👉 Con esto ya tenés una guía rápida dentro del proyecto.  
¿Querés que además te prepare un ejemplo de **Windows `.bat`** (para no depender de Git Bash) que funcione igual que el `generate_festival.sh`?
```
