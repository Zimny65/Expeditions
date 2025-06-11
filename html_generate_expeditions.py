from pathlib import Path
import geopandas as gpd
import folium
from folium.features import DivIcon
from folium import Element
import re

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

    # Dodaj font Oswald plus przesunięcie kontrolek
    m.get_root().header.add_child(Element("""
    <link href="https://fonts.googleapis.com/css2?family=Oswald&display=swap" rel="stylesheet">
    <style>
    .leaflet-top.leaflet-left {
        top: 70px !important;
    }
    </style>
    """))

    for idx, row in gdf.iterrows():
        lat, lon = row["lat"], row["lon"]
        counter = row.get("trail_counter", f"{idx+1:03d}")

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

def inject_custom_body_script(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    match = re.search(r'var (map_[a-f0-9]+) = L\.map\([^)]*\)', html)
    if not match:
        print("❌ Nie znaleziono zmiennej mapy w HTML.")
        return

    map_var_name = match.group(1)

    # Dodaj osobną linię z aliasem po definicji mapy
    insert_point = match.end()
    html = html[:insert_point] + f"\nvar map = {map_var_name};" + html[insert_point:]

    # Wczytaj szablon JS
    with open('html_dynamic_trail_layer.js', 'r', encoding='utf-8') as js_file:
        js_code = js_file.read().replace('{{MAP_VAR}}', map_var_name)

    script_tag = f"<script>\n{js_code}\n</script>"
    html = html.replace('</body>', script_tag + '\n</body>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dodano dynamiczny JS do {html_path}")

def main():
    gdf = load_geojson("output/colored.geojson")
    m = create_map_from_points(gdf)
    output_path = "C:/github/aktmamut.eu/maps/EXPEDITIONS.html"
    m.save(output_path)
    inject_custom_body_script(output_path)
    print(f"✅ Mapa zapisana jako {output_path}")

if __name__ == "__main__":
    main()
