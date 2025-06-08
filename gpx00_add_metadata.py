import os
import json
import gpxpy
import unicodedata
import re
from datetime import timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe z pliku .env
load_dotenv()

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "AKT Mamut Expeditions")
SHEET_TAB_NAME = os.getenv("SHEET_TAB_NAME", "ALL")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

GPX_DIR = "gpx"
OUTPUT_DIR = "output/geojson"

# Autoryzacja Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).worksheet(SHEET_TAB_NAME)
data = sheet.get_all_values()
header = data[0]
data_rows = data[1:]

def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower()
    name = name.replace(" ", "-").replace("--", "-")
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

    properties = {
        "nr": row[0],
        "date": row[1],
        "name": row[2],
        "mountains": row[3],
        "country": row[4],
        "gpx_url": row[5],
        "photo_album_url": row[6],
        "photo_stamp_url": row[7],
        "distance_km": float(row[8].replace(",", ".")) if row[8] else None,
        "ascent_m": int(row[9]) if row[9] else None,
        "duration_h": round(float(row[10].split(":")[0]) + float(row[10].split(":")[1]) / 60,2) if row[10] and ":" in row[10] else None,
        "got": row[11],
        "got_total": float(row[12].replace(",", ".")) if row[12] else None,
        "accomodation": row[13],
        "trail_counter": row[14],
        "exp_counter": row[15],
        "lat": float(row[16].replace(",", ".")) if row[16] else None,
        "lon": float(row[17].replace(",", ".")) if row[17] else None,
        "only_mountain": row[18],
        "participants": row[19],
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

def main():
    print("🔧 Tryb ręczny uruchomiony")
    gpx_filename = input("Podaj nazwę pliku GPX (np. 2025-06-08-wielki-krivan.gpx):\n> ").strip()
    base_name = normalize_name(gpx_filename.replace(".gpx", ""))

    # Wyciągamy datę i nazwę z pliku
    parts = base_name.split("-")
    if len(parts) < 4:
        print("❌ Nieprawidłowa nazwa pliku GPX")
        return

    date_part = "-".join(parts[:3])  # YYYY-MM-DD
    name_part = "-".join(parts[3:])  # Nazwa (może zawierać godzinę)

    found = None
    for row in data_rows:
        row_date = row[1].strip()
        row_name = normalize_name(row[2].strip())
        candidate = normalize_name(f"{row_date}-{row_name}")
        if candidate == f"{date_part}-{name_part}" or candidate.startswith(date_part):
            found = row
            break

    if not found:
        print(f"❌ Nie znaleziono dopasowania w arkuszu dla: {gpx_filename}")
        return

    generate_geojson(gpx_filename, found)

if __name__ == "__main__":
    main()
