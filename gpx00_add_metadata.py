import os
import json
import gpxpy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "AKT Mamut Expeditions")
SHEET_TAB_NAME = os.getenv("SHEET_TAB_NAME", "ALL")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

GPX_DIR = "gpx"
OUTPUT_DIR = "geojson/trails"

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

def generate_geojson(gpx_filename: str, row: list):
    gpx_path = os.path.join(GPX_DIR, gpx_filename)
    output_path = os.path.join(OUTPUT_DIR, gpx_filename.replace(".gpx", ".geojson"))

    if os.path.exists(output_path):
        print(f"⏩ Pominięto (istnieje): {output_path}")
        return

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
        "duration_h": round(float(row[10].split(":")[0]) + float(row[10].split(":")[1]) / 60, 2) if row[10] and ":" in row[10] else None,
        "got": row[11],
        "got_total": float(row[12].replace(",", ".")) if row[12] else None,
        "accomodation": row[13],
        "trail_counter": row[14],
        "exp_counter": row[15],
        "lat": float(row[16].replace(",", ".")) if row[16] else None,
        "lon": float(row[17].replace(",", ".")) if row[17] else None,
        "only_mountain": row[18],
        "participants": row[19],
        "gpx": row[20]
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
    gpx_files = [f for f in os.listdir(GPX_DIR) if f.endswith(".gpx")]
    print(f"🔍 Znaleziono {len(gpx_files)} plików GPX.")

    zapisano = 0
    pominieto = 0
    brak_w_arkuszu = 0

    for gpx_file in gpx_files:
        match = None
        for row in data_rows:
            if row[20].strip() == gpx_file:
                match = row
                break
        if match:
            output_path = os.path.join(OUTPUT_DIR, gpx_file.replace(".gpx", ".geojson"))
            if os.path.exists(output_path):
                print(f"⏩ Pominięto (istnieje): {output_path}")
                pominieto += 1
            else:
                generate_geojson(gpx_file, match)
                zapisano += 1
        else:
            print(f"⚠️ Brak dopasowania w arkuszu: {gpx_file}")
            brak_w_arkuszu += 1

    print("\n📊 Podsumowanie:")
    print(f"✅ Zapisano nowych plików: {zapisano}")
    print(f"⏩ Pomięto (istniejących): {pominieto}")
    print(f"❓ Brak dopasowania w arkuszu: {brak_w_arkuszu}")

if __name__ == "__main__":
    main()
