import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt  # tylko do debugowania, niekonieczne
import os

# ⚖️ Parametry
INPUT_PATH = "geojson/simplified_trails.geojson"
OUTPUT_PATH = "geojson/expeditions.geojson"
DISTANCE_THRESHOLD_METERS = 50  # odległość, poniżej której trasy uznajemy za sąsiadujące

# 🌈 Lista 10 kolorów (kontrastowych)
COLOR_PALETTE = [
    "#800000",  # Maroon
    "#FF0000",  # Red
    "#FFA500",  # Orange
    "#FFFF00",  # Yellow
    "#808000",  # Olive
    "#800080",  # Purple
    "#FF00FF",  # Fuchsia
    "#FFFFFF",  # White
    "#00FF00",  # Lime
    "#008000"   # Green
]
# COLOR_PALETTE = [
#     "#1f77b4",  # blue
#     "#ff7f0e",  # orange
#     "#2ca02c",  # green
#     "#d62728",  # red
#     "#9467bd",  # purple
#     "#8c564b",  # brown
#     "#e377c2",  # pink
#     "#7f7f7f",  # gray
#     "#bcbd22",  # olive
#     "#17becf",  # cyan
#     "#f781bf",  # light pink
#     "#999999",  # light gray
#     "#66c2a5",  # teal
#     "#fc8d62",  # coral
#     "#e78ac3"   # violet
# ]

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
