import os
import gpxpy
import geojson
from shapely.geometry import LineString
from tqdm import tqdm  # Dodajemy tqdm

gpx_folder = "gpx"
output_folder = "output"
output_geojson = os.path.join(output_folder, "all_trails.geojson")

features = []

gpx_files = [f for f in os.listdir(gpx_folder) if f.endswith(".gpx")]

for filename in tqdm(gpx_files, desc="GPX 01 MERGE", unit="plik"):
    filepath = os.path.join(gpx_folder, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    coords = [(pt.longitude, pt.latitude) for pt in segment.points]
                    if coords:
                        line = LineString(coords)
                        features.append(geojson.Feature(
                            geometry=line,
                            properties={"name": filename.replace(".gpx", "")}
                        ))
        except Exception as e:
            print(f"Błąd podczas przetwarzania {filename}: {e}")

collection = geojson.FeatureCollection(features)

with open(output_geojson, "w", encoding="utf-8") as f:
    geojson.dump(collection, f, ensure_ascii=False, indent=2)

print(f"\n✅ GPX 01 MERGE {len(features)} files to: {output_geojson}")
