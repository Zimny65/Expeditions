import geojson
from shapely.geometry import shape, mapping
from shapely.geometry.base import BaseGeometry
from tqdm import tqdm
from pathlib import Path

input_file = "output/all_trails.geojson"
output_file = "output/simplified_trails.geojson"

with open(input_file, "r", encoding="utf-8") as f:
    data = geojson.load(f)

simplified_features = []

for feature in tqdm(data["features"], desc="GPX 02 SIMPLIFYING", unit="trasa"):
    geom: BaseGeometry = shape(feature["geometry"])
    simplified = geom.simplify(0.0001, preserve_topology=False)
    simplified_features.append(geojson.Feature(
        geometry=mapping(simplified),
        properties=feature["properties"]
    ))

out = geojson.FeatureCollection(simplified_features)

with open(output_file, "w", encoding="utf-8") as f:
    geojson.dump(out, f, indent=2, ensure_ascii=False)

# Wyświetlenie absolutnej ścieżki zapisu
abs_path = Path(output_file).resolve()
print(f"✅ GPX 02 SIMPLIFYING - Output to: {abs_path}")
