import os
import json
import shutil
import requests
import pandas as pd
import folium
from folium.features import DivIcon
from folium.plugins import Fullscreen
from datetime import datetime
from dotenv import load_dotenv

def fetch_data_from_sheet(sheet_id, sheet_name, api_key):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{sheet_name}?alt=json&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if 'values' not in data:
        raise KeyError(f"Brak klucza 'values' dla arkusza {sheet_name}. Sprawdź klucz API i ID arkusza.")

    columns = data['values'][0]
    rows = data['values'][1:]
    df = pd.DataFrame(rows, columns=columns)
    df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
    df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
    df = df.dropna(subset=['LAT', 'LON']).reset_index(drop=True)
    return df

def load_geojson(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def add_html_header(map_object):
    header = (
        '<title>EXPEDITIONS</title>\n'
        '<link rel="icon" href="M32.png" type="image/png">'
    )
    map_object.get_root().html.add_child(folium.Element(header))

def generate_html_map(df, geojson_data, output_path):
    m = folium.Map(location=[df['LAT'].mean(), df['LON'].mean()], zoom_start=7, width="100%")
    folium.TileLayer(name='OpenStreetMap').add_to(m)

    for _, row in df.iterrows():
        lat, lon = float(row['LAT']), float(row['LON'])
        counter = row['Counter']
        trail_gpx = row['Trail GPX']

        if trail_gpx.startswith("http"):
            trail_gpx = f'<a href="{trail_gpx}" target="_blank">{trail_gpx}</a>'

        popup_html = """
        <div style="font-family: 'Oswald', sans-serif; font-size: 12px; color: black;">
            <table style="width: auto; border-collapse: collapse;">
        """
        for col in df.columns:
            val = trail_gpx if col == 'Trail GPX' else row[col]
            popup_html += f"""
                <tr>
                    <td style="font-weight: bold; padding: 4px; vertical-align: top;">{col}:</td>
                    <td style="padding: 4px; vertical-align: top;">{val}</td>
                </tr>
            """
        popup_html += "</table></div>"

        folium.Marker(
            location=[lat, lon],
            icon=DivIcon(
                icon_size=(24, 24),
                icon_anchor=(12, 12),
                html=f'<div style="font-size: 10px; font-family: Oswald, sans-serif; font-weight: bold; color: white; background-color: green; border-radius: 50%; border: 1px solid white; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">{counter}</div>'
            ),
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)

    group_layers = []
    for feature in geojson_data['features']:
        style = {
            'color': feature['properties'].get('color', 'gray'),
            'weight': 2,
            'opacity': 0.7
        }

        layer = folium.GeoJson(
            feature,
            style_function=lambda x, style=style: style
        )

        if feature['geometry']['type'] == "LineString":
            coords = feature['geometry']['coordinates']
            start = folium.CircleMarker([coords[0][1], coords[0][0]], radius=3, color="green", fill=True).add_to(m)
            end = folium.CircleMarker([coords[-1][1], coords[-1][0]], radius=3, color="blue", fill=True).add_to(m)

            if 'name' in feature['properties']:
                layer.add_child(folium.Tooltip(feature['properties']['name'], sticky=True))

            group = folium.map.FeatureGroup()
            group.add_child(layer)
            group.add_child(start)
            group.add_child(end)
            group_layers.append(group)

    for g in group_layers:
        g.add_to(m)

    Fullscreen().add_to(m)

    style = """
        <style>
        .leaflet-container { width: 100vw; height: 100vh; }
        .leaflet-control-zoom { transform: translateY(160px); }
        .leaflet-control-attribution { display: none; }
        .leaflet-control-minimap { transform: translateY(-60px); }
        </style>
    """
    m.get_root().html.add_child(folium.Element(style))
    add_html_header(m)
    m.save(output_path)

if __name__ == "__main__":
    load_dotenv()
    sheet_id = '1z3ceJOc6PpKWGqIxMi6P4Ij1i37rcXIx3P_VIWrGpN0'
    sheet_name = 'ALL'
    api_key = os.getenv("GOOGLE_API_KEY")

    output_directory = "C:\\github\\aktmamut.eu\\maps"
    archive_directory = "C:\\github\\Expeditions\\archive"
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(archive_directory, exist_ok=True)

    output_filename = "EXPEDITIONS.html"
    output_path = os.path.join(output_directory, output_filename)
    archive_path = os.path.join(archive_directory, f"EXPEDITIONS-{datetime.today().date()}.html")

    df = fetch_data_from_sheet(sheet_id, sheet_name, api_key)
    geojson_data = load_geojson("C:\\github\\Expeditions\\output\\colored.geojson")
    generate_html_map(df, geojson_data, output_path)

    shutil.copyfile(output_path, archive_path)

    print(f"✅ HTML 01 EXPEDITIONS - Output to: {output_path}")
    print(f"✅ HTML 01 EXPEDITIONS - Archive to: {archive_path}")
