import os
import json
import gpxpy
import unicodedata
import re
from datetime import datetime
import gspread
from tqdm import tqdm
from oauth2client.service_account import ServiceAccountCredentials

# Konfiguracja
GOOGLE_SHEET_NAME = "AKT Mamut Expeditions"
SHEET_TAB_NAME = "ALL"
GPX_DIR = "gpx"
OUTPUT_DIR = "output/geojson"

# Autoryzacja Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).worksheet(SHEET_TAB_NAME)
data = sheet.get_all_values()
header = data[0]
data_rows = data[1:]

def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower()
    name = name.replace("–", "-").replace("—", "-").replace(" ", "-")
    name = re.sub(r"-+", "-", name)
    name = re.sub(r"[^a-z0-9\-]", "", name)
    return name

def generate_geojson(gpx_filename: str, row: list):
    gpx_path = os.path.join(GPX_DIR, gpx_filename)
    output_path = os.path.join(OUTPUT_DIR, gpx_filename.replace(".gpx", ".geojson"))

    if os.path.exists(output_path):
        return  # Pomijanie już przetworzonych plików

    with open(gpx_path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)

    track = gpx.tracks[0]
    segment = track.segments[0]

    coords = [[point.longitude, point.latitude, point.elevation] for point in segment.points]

    duration_h = None
    if row[10] and ":" in row[10]:
        try:
            h, m = row[10].split(":")
            duration_h = round(float(h) + float(m) / 60, 2)
        except Exception:
            duration_h = None

    properties = {
        "name": row[2],
        "distance_km": float(row[8].replace(",", ".")) if row[8] else None,
        "ascent_m": int(row[9]) if row[9] else None,
        "duration_h": duration_h,
        "got": row[11],
        "got_total": float(row[12].replace(",", ".")) if row[12] else None,
        "accomodation": row[13],
        "trail_counter": row[14],
        "exp_counter": row[15],
        "lat": float(row[16].replace(",", ".")) if row[16] else None,
        "lon": float(row[17].replace(",", ".")) if row[17] else None,
        "only_mountain": row[18],
        "participants": row[19],
        "wikiloc_url": row[6],
        "photo_album_url": row[7],
        "photo_stamp_url": row[8],
        "country": row[4],
        "mountains": row[3],
        "date": row[1],
        "trail_gpx_url": row[5],
        "mapycz_gpx_url": row[20] if len(row) > 20 else ""
    }

    geojson = {
        "type": "Feature",
        "properties": properties,
        "geometry": {
            "type": "LineString",
            "coordinates": coords
        }
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"✅ Zapisano: {output_path}")

# Automatyczne przetwarzanie wsadowe
sheet_map = {}
for row in data_rows:
    try:
        date_str = row[1]
        name = row[2]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        prefix = dt.strftime("%Y-%m-%d")
        full_key = normalize_name(f"{prefix}-{name}")
        sheet_map[full_key] = row
    except Exception:
        continue

# Lista plików GPX
gpx_files = [f for f in os.listdir(GPX_DIR) if f.endswith(".gpx")]
print(f"🔍 Znaleziono {len(gpx_files)} plików GPX")
os.makedirs(OUTPUT_DIR, exist_ok=True)

for f in tqdm(gpx_files, desc="Przetwarzanie GPX", unit="plik"):
    key = normalize_name(f.replace(".gpx", ""))
    if key in sheet_map:
        try:
            generate_geojson(f, sheet_map[key])
        except Exception as e:
            print(f"❌ Błąd przy {f}: {e}")
    else:
        print(f"❌ Brak dopasowania w arkuszu: {f} (klucz: {key})")

print("\n😊 Gotowe!")
