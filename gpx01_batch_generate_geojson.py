import os
import unicodedata
import gpxpy
import json
import gspread
from datetime import datetime
from tqdm import tqdm
from gpx00_add_metadata import generate_geojson, normalize_name
from oauth2client.service_account import ServiceAccountCredentials

# Ścieżki
GPX_DIR = 'gpx'
OUTPUT_DIR = 'output/geojson'
GOOGLE_SHEET_NAME = 'AKT Mamut Expeditions'
SHEET_TAB_NAME = 'ALL'

# Autoryzacja do Google Sheets
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(credentials)
sheet = client.open(GOOGLE_SHEET_NAME).worksheet(SHEET_TAB_NAME)
all_rows = sheet.get_all_values()

# Nagłówki z arkusza
headers = all_rows[0]
data_rows = all_rows[1:]

# Funkcja pomocnicza do porównywania nazw

def normalize(text):
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.replace(' ', '-').replace('\u0142', 'l').replace('\u00f3', 'o')
    return text

# Mapowanie nazw plików do wierszy arkusza
sheet_map = {}
for row in data_rows:
    date_str = row[1]
    name = row[2]
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        prefix = dt.strftime('%Y-%m-%d')
        full_key = normalize(f"{prefix}-{name}")
        sheet_map[full_key] = row
    except Exception as e:
        continue

# Lista plików GPX
gpx_files = [f for f in os.listdir(GPX_DIR) if f.endswith('.gpx')]
print(f"🔍 Znaleziono {len(gpx_files)} plików GPX")

# Tworzymy katalog output, jeśli nie istnieje
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Przetwarzanie
for f in tqdm(gpx_files, desc="Przetwarzanie GPX", unit="plik"):
    output_path = os.path.join(OUTPUT_DIR, f.replace('.gpx', '.geojson'))
    if os.path.exists(output_path):
        continue  # pomiń jeśli już istnieje

    key = f.replace('.gpx', '')
    if key in sheet_map:
        try:
            generate_geojson(f, sheet_map[key])
        except Exception as e:
            print(f"❌ Błąd przy {f}: {e}")
    else:
        print(f"❌ Brak dopasowania w arkuszu: {f}")

print("\n😊 Gotowe!")
