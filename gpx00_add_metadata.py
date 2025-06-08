import os
import json
import gpxpy
import unicodedata
import re
from datetime import timedelta
import gspread
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
    name = name.strip()
    name = name.replace(" ", "-")
    name = re.sub(r"-+", "-", name)  # usunięcie wielu myślników
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
        "name": row[2],
        "distance_km": float(row[8].replace(",", ".")) if row[8] else None,
        "ascent_m": int(row[9]) if row[9] else None,
        "duration_h": round(sum(
            float(t.split(":"[0])) + float(t.split(":")[1]) / 60
            for t in [row[10]] if ":" in t
        ), 2) if row[10] else None,
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

def main():
    try:
        gpx_filename = input("Podaj nazwę pliku GPX (np. 2025-06-08-wielki-krivan.gpx):\n> ").strip()
    except EOFError:
        print("❌ Błąd: input() nie zadziałał. Uruchom skrypt z terminala lub jako standalone.")
        return

    found = None

    # Rozbij na datę i nazwę
    parts = gpx_filename.replace(".gpx", "").split("-")
    if len(parts) < 4:
        print(f"❌ Niepoprawna nazwa pliku: {gpx_filename}")
        return

    date_str = "-".join(parts[:3])
    trail_name = "-".join(parts[4:])  # pomijamy godzinę
    normalized_input = normalize_name(f"{date_str}-{trail_name}")

    for row in data_rows:
        row_date = row[1].strip()
        row_name = row[2].strip()
        normalized_sheet = normalize_name(f"{row_date}-{row_name}")
        if normalized_input == normalized_sheet:
            found = row
            break

    if not found:
        print(f"❌ Nie znaleziono dopasowania w arkuszu dla: {gpx_filename}")
        print(f"🔍 Szukałem: {normalized_input}")
        return

    generate_geojson(gpx_filename, found)
