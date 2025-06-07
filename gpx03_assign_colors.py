import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt  # tylko do debugowania, niekonieczne
import os

# ⚖️ Parametry
INPUT_PATH = "C:/github/Expeditions/output/simplified.geojson"
OUTPUT_PATH = "C:/github/Expeditions/output/colored.geojson"
DISTANCE_THRESHOLD_METERS = 50  # odległość, poniżej której trasy uznajemy za sąsiadujące

# 🌈 Lista 10 kolorów (kontrastowych)
COLOR_PALETTE = [
    "#FF0000",  # Red
    "#8B0000",  # DarkRed
    "#FF4500",  # OrangeRed
    "#800080"   # Purple
]

print("✅ Wczytywanie danych...")
gdf = gpd.read_file(INPUT_PATH)

# Upewnij się, że geometrie to LineString
gdf = gdf[gdf.geometry.type == "LineString"].reset_index(drop=True)

# Konwersja do układu metrycznego (Web Mercator)
gdf = gdf.to_crs(epsg=3857)

# 🔄 Tworzymy graf konfliktów
print("🚀 Budowanie grafu kolizyjnego...")
G = nx.Graph()
G.add_nodes_from(gdf.index)

# Spatial index przyspiesza porównania
sindex = gdf.sindex

for i, geom in enumerate(gdf.geometry):
    possible_matches_index = list(sindex.intersection(geom.buffer(DISTANCE_THRESHOLD_METERS).bounds))
    for j in possible_matches_index:
        if i >= j:
            continue  # unikamy duplikatów i porównań ze sobą
        if geom.distance(gdf.geometry[j]) < DISTANCE_THRESHOLD_METERS:
            G.add_edge(i, j)

# 🎭 Przypisanie kolorów metodą "graph coloring"
print(f"🎨 Przypisywanie kolorów ({len(COLOR_PALETTE)} dostępnych)...")
coloring = nx.coloring.greedy_color(G, strategy="largest_first")

# Mapuj numer koloru na HEX z palety
def get_hex_color(color_index):
    return COLOR_PALETTE[color_index % len(COLOR_PALETTE)]

gdf["color"] = gdf.index.map(lambda idx: get_hex_color(coloring.get(idx, 0)))

# Powrót do WGS84 przed zapisem
gdf = gdf.to_crs(epsg=4326)

# Zapis do pliku
print(f"🔳 Zapis do: {OUTPUT_PATH}")
gdf.to_file(OUTPUT_PATH, driver="GeoJSON")
print("✅ Gotowe!")
