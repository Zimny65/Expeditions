from pathlib import Path
import geopandas as gpd
import folium
from folium.features import DivIcon
from folium import Element
import re

INPUT_GEOJSON = "geojson/expeditions.geojson"
OUTPUT_EXPEDITION = "C:/github/aktmamut.eu/maps/EXPEDITIONS.html"

def load_geojson(filepath: str) -> gpd.GeoDataFrame:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Plik nie istnieje: {filepath}")
    gdf = gpd.read_file(filepath)
    print(f"Wczytano {len(gdf)} obiektów z pliku: {filepath}")
    return gdf

def create_map_from_points(gdf):
    if "lat" not in gdf.columns or "lon" not in gdf.columns:
        raise ValueError("GeoDataFrame musi zawierać kolumny 'lat' i 'lon'")

    lat_center = gdf["lat"].mean()
    lon_center = gdf["lon"].mean()
    m = folium.Map(location=[lat_center, lon_center], zoom_start=7, tiles="OpenStreetMap")
        
    for idx, row in gdf.iterrows():
        lat, lon = row["lat"], row["lon"]
        counter = row.get("trail_counter", f"{idx+1:03d}")

        # Generowanie popup - dane z expeditions.geojson
        popup_html = f"""
        <div style="font-family: 'Oswald', sans-serif; font-size: 12px; color: black; background-color: white;">
            <table style="width: auto; border-collapse: collapse;">
                <tr><th style="text-align: left; padding-right: 6px;">Trail nr:</th><td style="padding-left: 6px;">{row.get('nr', '')}</td></tr>
                <tr><th style="text-align: left;">Date:</th><td style="padding-left: 6px;">{row.get('date', '')}</td></tr>
                <tr><th style="text-align: left;">Trail name:</th><td style="padding-left: 6px;">{row.get('name', '')}</td></tr>
                <tr><th style="text-align: left;">Mountains:</th><td style="padding-left: 6px;">{row.get('mountains', '')}</td></tr>
                <tr><th style="text-align: left;">Country:</th><td style="padding-left: 6px;">{row.get('country', '')}</td></tr>
                <tr><th style="text-align: left;">Distance:</th><td style="padding-left: 6px;">{row.get('distance_km', '')} km</td></tr>
                <tr><th style="text-align: left;">Up:</th><td style="padding-left: 6px;">{row.get('ascent_m', '')} m</td></tr>
                <tr><th style="text-align: left;">Time:</th><td style="padding-left: 6px;">{row.get('duration_h', '')} h</td></tr>
                <tr><th style="text-align: left;">GOT:</th><td style="padding-left: 6px;">{row.get('got', '')}</td></tr>
                <tr><th style="text-align: left;">Counter:</th><td style="padding-left: 6px;">{row.get('trail_counter', '')}</td></tr>
                <tr><th style="text-align: left;">Participants:</th><td style="padding-left: 6px;">{row.get('participants', '')}</td></tr>
                <tr><th style="text-align: left;">GPX:</th><td style="padding-left: 6px;"><a href="{row.get('gpx_url', '#')}" target="_blank">Wikiloc Link</a></td></tr>
            </table>
        </div>
        """

        # Generowanie zielonych kółeczek z numerami tras
        folium.Marker(
            location=[lat, lon],
            icon=DivIcon(
                icon_size=(24, 24),
                icon_anchor=(12, 12),
                html=f'''
                <div style="
                    font-size: 10px;
                    font-family: Oswald, sans-serif;
                    font-weight: bold;
                    color: white;
                    background-color: green;
                    border-radius: 50%;
                    border: 1px solid white;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;">
                    {counter}
                </div>'''
            ),
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
        
    return m

# 🖼️ Dodaj favicon i tytuł
def add_html_header(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace(
        '<head>',
        f'<head>\n    <title>{"EXPEDITIONS"}</title>\n    <link rel="icon" href="M32.png" type="image/png">'
    )
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    gdf = load_geojson(INPUT_GEOJSON)
    m = create_map_from_points(gdf)
    m.save(OUTPUT_EXPEDITION)
    add_html_header(OUTPUT_EXPEDITION)
    print(f"✅ Mapa zapisana jako {OUTPUT_EXPEDITION}")

if __name__ == "__main__":
    main()
