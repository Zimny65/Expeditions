import geojson
import geopandas as gpd
from shapely.geometry import shape
from tqdm import tqdm
from pathlib import Path

input_file = "geojson/all_trails.geojson"
output_file = "geojson/simplified_trails.geojson"

# Wczytaj dane wejściowe jako GeoJSON
with open(input_file, "r", encoding="utf-8") as f:
    data = geojson.load(f)

features = []
for feature in tqdm(data["features"], desc="GPX 02 SIMPLIFYING", unit="trasa"):
    geom = shape(feature["geometry"])
    simplified = geom.simplify(0.0001, preserve_topology=False) # Uproszczenie trasy do punktów co 10 metrów
    features.append({
        "geometry": simplified,
        **feature["properties"]
    })

# Utwórz GeoDataFrame i zapisz w formacie GeoJSON
gdf = gpd.GeoDataFrame(features, geometry="geometry", crs="EPSG:4326")
gdf.to_file(output_file, driver="GeoJSON")

print(f"✅ GPX 02 SIMPLIFYING - Output to: {Path(output_file).resolve()}")
