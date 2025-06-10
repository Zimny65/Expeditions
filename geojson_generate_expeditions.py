# all_generate_script.py

import os
import json
import shutil
import gpxpy
import gspread
import geopandas as gpd
import networkx as nx
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# ==== USTAWIENIA ====
load_dotenv()

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "AKT Mamut Expeditions")
SHEET_TAB_NAME = os.getenv("SHEET_TAB_NAME", "ALL")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

GPX_DIR = "gpx"
TRAILS_DIR = "geojson/trails"
MERGED_FILE = "geojson/all_trails.geojson"
SIMPLIFIED_FILE = "geojson/simplified_trails.geojson"
FINAL_FILE = "geojson/expeditions.geojson"
EXPORT_PATH = "C:/github/aktmamut.eu/maps/expeditions.geojson"

DISTANCE_THRESHOLD_METERS = 50
COLOR_PALETTE = [
    "#800000", "#FF0000", "#FFA500", "#FFFF00", "#808000",
    "#800080", "#FF00FF", "#FFFFFF", "#00FF00", "#008000"
]

# ==== KROK 1: Wczytanie danych z Google Sheets ====
print("\n📥 KROK 1: Odczyt arkusza Google Sheets")
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

os.makedirs(TRAILS_DIR, exist_ok=True)

# ==== KROK 2: Konwersja GPX -> GeoJSON z metadanymi ====
print("\n📍 KROK 2: Konwersja GPX -> GeoJSON")
gpx_files = [f for f in os.listdir(GPX_DIR) if f.endswith(".gpx")]
for gpx_file in gpx_files:
    match = next((row for row in data_rows if row[20].strip() == gpx_file), None)
    if not match:
        print(f"⚠️ Brak danych w arkuszu: {gpx_file}")
        continue

    gpx_path = os.path.join(GPX_DIR, gpx_file)
    output_path = os.path.join(TRAILS_DIR, gpx_file.replace(".gpx", ".geojson"))
    if os.path.exists(output_path):
        print(f"⏩ Pominięto (istnieje): {output_path}")
        continue

    with open(gpx_path, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)

    track = gpx.tracks[0]
    segment = track.segments[0]
    coords = [[p.longitude, p.latitude, p.elevation] for p in segment.points]

    properties = dict(zip([
        "nr", "date", "name", "mountains", "country", "gpx_url",
        "photo_album_url", "photo_stamp_url", "distance_km", "ascent_m",
        "duration_h", "got", "got_total", "accomodation", "trail_counter",
        "exp_counter", "lat", "lon", "only_mountain", "participants", "gpx"
    ], match + [None] * (21 - len(match))))

    if properties["distance_km"]:
        properties["distance_km"] = float(properties["distance_km"].replace(",", "."))
    if properties["ascent_m"]:
        properties["ascent_m"] = int(properties["ascent_m"])
    if properties["duration_h"] and ":" in properties["duration_h"]:
        h, m = map(int, properties["duration_h"].split(":"))
        properties["duration_h"] = round(h + m / 60, 2)
    if properties["got_total"]:
        properties["got_total"] = float(properties["got_total"].replace(",", "."))
    if properties["lat"]:
        properties["lat"] = float(properties["lat"].replace(",", "."))
    if properties["lon"]:
        properties["lon"] = float(properties["lon"].replace(",", "."))

    geojson = {
        "type": "Feature",
        "properties": properties,
        "geometry": {"type": "LineString", "coordinates": coords}
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"✅ Zapisano: {output_path}")

# ==== KROK 3: Połączenie plików ====
print("\n📚 KROK 3: Scalanie GeoJSON")
features = []
for file in tqdm(os.listdir(TRAILS_DIR), desc="Scalanie", unit="plik"):
    path = os.path.join(TRAILS_DIR, file)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if data["type"] == "Feature":
            features.append(data)
        elif data["type"] == "FeatureCollection":
            features.extend(data["features"])

merged = {"type": "FeatureCollection", "features": features}
with open(MERGED_FILE, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
print(f"✅ Zapisano do: {MERGED_FILE}")

# ==== KROK 4: Upraszczanie ====
print("\n🧪 KROK 4: Upraszczanie geometrii")
gdf = gpd.read_file(MERGED_FILE)
gdf = gdf[gdf.geometry.type == "LineString"]
gdf = gdf.to_crs(epsg=3857)
gdf["geometry"] = gdf["geometry"].simplify(tolerance=10)
gdf = gdf.to_crs(epsg=4326)
gdf.to_file(SIMPLIFIED_FILE, driver="GeoJSON")
print(f"✅ Zapisano do: {SIMPLIFIED_FILE}")

# ==== KROK 5: Przypisywanie kolorów ====
print("\n🎨 KROK 5: Kolorowanie tras")
gdf = gpd.read_file(SIMPLIFIED_FILE)
gdf = gdf[gdf.geometry.type == "LineString"].reset_index(drop=True)
gdf = gdf.to_crs(epsg=3857)

G = nx.Graph()
G.add_nodes_from(gdf.index)
sindex = gdf.sindex
for i, geom in enumerate(gdf.geometry):
    nearby = list(sindex.intersection(geom.buffer(DISTANCE_THRESHOLD_METERS).bounds))
    for j in nearby:
        if i >= j:
            continue
        if geom.distance(gdf.geometry[j]) < DISTANCE_THRESHOLD_METERS:
            G.add_edge(i, j)

coloring = nx.coloring.greedy_color(G, strategy="largest_first")

def color_hex(idx):
    return COLOR_PALETTE[coloring.get(idx, 0) % len(COLOR_PALETTE)]

gdf["color"] = gdf.index.map(color_hex)
gdf = gdf.to_crs(epsg=4326)
gdf.to_file(FINAL_FILE, driver="GeoJSON")
print(f"✅ Zapisano do: {FINAL_FILE}")

# ==== KROK 6: Kopiowanie pliku do katalogu Netlify ====
print("\n📤 KROK 6: Kopiowanie do maps/")
os.makedirs(Path(EXPORT_PATH).parent, exist_ok=True)
shutil.copy2(FINAL_FILE, EXPORT_PATH)
print(f"✅ Sfinalizowano: {EXPORT_PATH}")
