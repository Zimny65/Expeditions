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

    # Dodaj font Oswald
    m.get_root().html.add_child(Element(
        '<link href="https://fonts.googleapis.com/css2?family=Oswald&display=swap" rel="stylesheet">'
    ))

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

def add_html_header(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        html_content = f.read()

    if '<title>EXPEDITIONS</title>' in html_content:
        print("Nagłówek już istnieje, pomijam.")
        return

    html_content = html_content.replace(
        '<head>',
        '''<head>
    <title>EXPEDITIONS</title>
    <link rel="icon" href="M32.png" type="image/png">
    <link href="https://fonts.googleapis.com/css2?family=Oswald&display=swap" rel="stylesheet">'''
    )

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Dodano favicon i tytuł do: {filename}")

def inject_custom_body_script(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    match = re.search(r'var (map_[a-f0-9]+) = L\.map\(', html)
    if not match:
        print("❌ Nie znaleziono zmiennej mapy w HTML.")
        return

    map_var_name = match.group(1)

    custom_script = f"""<script>
        let allGpxLayer = null;

        window.addEventListener("DOMContentLoaded", function () {{
            function toggleAllGpxLayer() {{
                const map = {map_var_name};
                const zoom = map.getZoom();

                if (zoom >= 10 && !allGpxLayer) {{
                    fetch('../gpx/colored.geojson')
                        .then(res => res.json())
                        .then(data => {{
                            const groupLayers = [];

                            L.geoJSON(data, {{
                                style: function(feature) {{
                                    return {{
                                        color: feature.properties.color || 'gray',
                                        weight: 2,
                                        opacity: 0.7
                                    }};
                                }},
                                onEachFeature: function (feature, layer) {{
                                    if (feature.geometry.type === "LineString") {{
                                        const coords = feature.geometry.coordinates;

                                        if (feature.properties && feature.properties.name) {{
                                            layer.bindTooltip(feature.properties.name, {{ sticky: true }});
                                        }}

                                        layer.on({{
                                            mouseover: function () {{
                                                layer.setStyle({{ weight: 8, color: '#000000' }});
                                            }},
                                            mouseout: function () {{
                                                layer.setStyle({{
                                                    weight: 2,
                                                    color: feature.properties.color || 'gray'
                                                }});
                                            }}
                                        }});

                                        const startMarker = L.circleMarker([coords[0][1], coords[0][0]], {{
                                            radius: 3,
                                            color: "red",
                                            fillColor: "red",
                                            fillOpacity: 1
                                        }});
                                        const endMarker = L.circleMarker([coords[coords.length - 1][1], coords[coords.length - 1][0]], {{
                                            radius: 3,
                                            color: "red",
                                            fillColor: "red",
                                            fillOpacity: 1
                                        }});

                                        const group = L.layerGroup([layer, startMarker, endMarker]);
                                        groupLayers.push(group);
                                    }}
                                }}
                            }});

                            allGpxLayer = L.layerGroup(groupLayers);
                            allGpxLayer.addTo(map);
                        }});
                }}

                if (zoom < 10 && allGpxLayer) {{
                    map.removeLayer(allGpxLayer);
                    allGpxLayer = null;
                }}
            }}

            const map = {map_var_name};
            map.on('zoomend', toggleAllGpxLayer);
            toggleAllGpxLayer();
        }});
    </script>"""

    html = html.replace('</body>', custom_script + '\n</body>')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Dodano JS do {html_path} – dynamiczne trasy od zoom 10.")

def main():
    gdf = load_geojson("output/colored.geojson")
    m = create_map_from_points(gdf)
    m.save("EXPEDITIONS.html")
    add_html_header("EXPEDITIONS.html")
    inject_custom_body_script("EXPEDITIONS.html")
    print("✅ Mapa zapisana jako EXPEDITIONS.html")

if __name__ == "__main__":
    main()
