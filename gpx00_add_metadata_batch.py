import os
from gpx00_add_metadata import normalize_name, generate_geojson, data_rows

# Ścieżki folderów
GPX_DIR = r"c:\\github\\Expeditions\\gpx"
OUTPUT_DIR = r"c:\\github\\Expeditions\\output\\geojson"

# Pobranie listy plików
all_gpx_files = [f for f in os.listdir(GPX_DIR) if f.lower().endswith(".gpx")]
all_geojson_files = {f.replace(".geojson", ".gpx") for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(".geojson")}

# Lista do raportu
processed = []
skipped = []
not_found = []

for gpx_file in all_gpx_files:
    if gpx_file in all_geojson_files:
        skipped.append(gpx_file)
        continue

    base_name = normalize_name(gpx_file.replace(".gpx", ""))
    parts = base_name.split("-")
    if len(parts) < 4:
        not_found.append(gpx_file)
        continue

    date_part = "-".join(parts[:3])
    name_part = "-".join(parts[3:])

    found = None
    for row in data_rows:
        row_date = row[1].strip()
        row_name = normalize_name(row[2].strip())
        candidate = normalize_name(f"{row_date}-{row_name}")
        if candidate == f"{date_part}-{name_part}" or candidate.startswith(date_part):
            found = row
            break

    if found:
        try:
            generate_geojson(gpx_file, found)
            processed.append(gpx_file)
        except Exception as e:
            print(f"❌ Błąd podczas przetwarzania {gpx_file}: {e}")
    else:
        not_found.append(gpx_file)

# Raport
print("\n📊 Podsumowanie:")
print(f"✅ Przetworzono: {len(processed)}")
print(f"ℹ️  Pomięto (istniejące): {len(skipped)}")
print(f"❌ Nie znaleziono w arkuszu: {len(not_found)}")

if not_found:
    print("\nNieprzetworzone pliki bez dopasowania:")
    for f in not_found:
        print(" -", f)
