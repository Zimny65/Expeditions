import os
import json
from pathlib import Path
from tqdm import tqdm

INPUT_DIR = "output/geojson"
OUTPUT_FILE = "output/all_trails.geojson"

features = []

# Znajdź wszystkie pliki .geojson w katalogu
geojson_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".geojson")]

print(f"🔍 Znaleziono {len(geojson_files)} plików do połączenia...")

for filename in tqdm(geojson_files, desc="GPX 01 MERGE", unit="plik"):
    filepath = os.path.join(INPUT_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data["type"] == "Feature":
                features.append(data)
            elif data["type"] == "FeatureCollection":
                features.extend(data["features"])
            else:
                print(f"⚠️ Nieoczekiwany typ w pliku {filename}")
    except Exception as e:
        print(f"❌ Błąd podczas przetwarzania {filename}: {e}")

# Zbuduj zbiorczy obiekt GeoJSON
merged = {
    "type": "FeatureCollection",
    "features": features
}

# Zapisz wynik
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

abs_path = Path(OUTPUT_FILE).resolve()
print(f"\n✅ GPX 01 MERGE zakończone — zapisano do: {abs_path}")
