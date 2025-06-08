import gpxpy
import geojson
import os
import unicodedata
import re
from datetime import timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === USTAWIENIA ===
GPX_FOLDER = "gpx"
GEOJSON_FOLDER = "output/geojson"
GOOGLE_SHEET_NAME = "AKT Mamut Expeditions"
SHEET_TAB_NAME = "ALL"

# === FUNKCJE ===

def normalize(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', '-', text.lower())

def hhmm_to_hours(text):
    h, m = map(int, text.strip().split(':'))
    return round(h + m / 60.0, 2)

def match_gpx_to_row(gpx_filename, rows):
    basename = os.path.basename(gpx_filename).lower()
    
    # Usuń rozszerzenie i podziel po myślnikach
    name_parts = os.path.splitext(basename)[0].split("-")
    
    # Wyciągamy datę
    if len(name_parts) < 5:
        return None
    date = "-".join(name_parts[0:3])  # YYYY-MM-DD
    trail_part = "-".join(name_parts[5:])  # pomijamy godziny
    
    for row in rows:
        sheet_date = row[1]  # kolumna B
        sheet_trail = row[2]  # kolumna C
        expected = normalize(f"{sheet_date}-{sheet_trail}")
        actual = normalize(f"{date}-{trail_part}")
        if expected == actual:
            return row
    return None

def parse_gpx_file(gpx_path):
    with open(gpx_path, 'r', encoding='utf-8') as f:
        gpx = gpxpy.parse(f)
    coords = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coords.append((point.longitude, point.latitude, point.elevation))
    return coords

def main():
    print("Podaj nazwę pliku GPX (np. 2025-06-08-wielki-krivan.gpx):")
    gpx_name = input("> ").strip()
    gpx_path = os.path.join(GPX_FOLDER, gpx_name)

    if not os.path.exists(gpx_path):
        print(f"❌ Plik nie istnieje: {gpx_path}")
        return

    # === Autoryzacja Google Sheets ===
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).worksheet(SHEET_TAB_NAME)
    rows = sheet.get_all_values()[1:]  # pomijamy nagłówek

    # === Dopasowanie metadanych ===
    row = match_gpx_to_row(gpx_name, rows)
    if not row:
        print("❌ Nie znaleziono dopasowania w arkuszu.")
        return

    trail_name = row[2]
    distance_km = float(row[6].replace(",", "."))
    ascent_m = int(float(row[7].replace(",", ".")))
    duration_h = hhmm_to_hours(row[8])
    wikiloc_url = row[5]

    # === Parsowanie GPX ===
    coords = parse_gpx_file(gpx_path)
    if not coords:
        print("❌ Brak punktów w GPX.")
        return

    geometry = geojson.LineString(coords)
    feature = geojson.Feature(
        geometry=geometry,
        properties={
            "name": trail_name,
            "distance_km": distance_km,
            "ascent_m": ascent_m,
            "duration_h": duration_h,
            "wikiloc_url": wikiloc_url
        }
    )

    # === Zapis GeoJSON ===
    os.makedirs(GEOJSON_FOLDER, exist_ok=True)
    base = os.path.splitext(gpx_name)[0]
    geojson_path = os.path.join(GEOJSON_FOLDER, f"{base}.geojson")

    with open(geojson_path, 'w', encoding='utf-8') as f:
        geojson.dump(feature, f, indent=2)

    print(f"✅ Zapisano: {geojson_path}")

if __name__ == "__main__":
    main()
