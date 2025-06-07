import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from datetime import datetime
import re

# Ścieżki
base_dir = Path(__file__).parent
gpx_dir = base_dir / "gpx"
output_dir = base_dir / "output"
archive_dir = base_dir / "archive"
expeditions_html = base_dir / "EXPEDITIONS.html"

# Ścieżki do Netlify (GitHub)
netlify_dir = Path("C:/github/aktmamut.eu")
netlify_maps = netlify_dir / "maps" / "EXPEDITIONS.html"
netlify_gpx = netlify_dir / "gpx" / "simplified_trails.geojson"

# 1. Scalanie GPX → GeoJSON
subprocess.run(["python", "gpx01_merge_gpx_to_geojson.py"], check=True)

# 2. Upraszczanie GeoJSON
subprocess.run(["python", "gpx02_simplify_geojson.py"], check=True)

# 3. Generowanie EXPEDITIONS.html
subprocess.run(["python", "html01_generate_expeditions.py"], check=True)

# # 4. Archiwizacja HTML
timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
# archive_path = archive_dir / f"{timestamp}.html"
# shutil.copy2(expeditions_html, archive_path)
# print(f"✅ Zarchiwizowano do: {archive_path}")

# 5. Kopiowanie do Netlify (HTML) + GeoJSON)
# shutil.copy2(expeditions_html, netlify_maps)
# print(f"✅ Skopiowano HTML do Netlify: {netlify_maps}")

# 5. Kopiowanie do Netlify (GeoJSON)
simplified_geojson = output_dir / "simplified_trails.geojson"
shutil.copy2(simplified_geojson, netlify_gpx)
print(f"✅ GPX 02 SIMPLIFYING - Copy GeoJSON to: {netlify_gpx}")

# 6. Stopka z wersją
index_path = r'C:\github\aktmamut.eu\index.html'
now = datetime.now().strftime("v %Y-%m-%d %H:%M")

with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Jeśli <span id="version-label"> istnieje — tylko aktualizujemy wersję
if 'id="version-label"' in html:
    html = re.sub(
        r'(<span id="version-label".*?>)(.*?)(</span>)',
        rf'\1{now}\3',
        html,
        flags=re.DOTALL
    )

# 2. Jeśli jest tylko <p> z tekstem typu "&copy; 2015 AKT MAMUT v ..." — zamieniamy cały <div class="footer-content">
elif re.search(r'<div class="footer-content">\s*<p>.*?&copy; 2015 AKT MAMUT.*?</p>\s*</div>', html, re.DOTALL):
    html = re.sub(
    r'<div class="footer-content">\s*<p>.*?&copy; 2015 AKT MAMUT.*?</p>\s*</div>',
    f'''
<div class="footer-content" style="display: flex; justify-content: center; align-items: center; position: relative; height: 50px; background-color: #222; color: white;">
    <p style="margin: 0;">&copy; 2015 AKT MAMUT</p>
    <span id="version-label" style="position: absolute; right: 20px; font-size: 0.9em; color: #ccc;">{now}</span>
</div>
''',
    html,
    flags=re.DOTALL
)

else:
    print("⚠️ Nie znaleziono rozpoznawalnej stopki — upewnij się, że masz <div class=\"footer-content\"><p>...</p></div>.")

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 7. Git commit & push (zakomentowane)
subprocess.run(["git", "add", "."], cwd=netlify_dir, check=True)
subprocess.run(["git", "commit", "-m", f"GITHUB COMMIT {timestamp}"], cwd=netlify_dir, check=True)
subprocess.run(["git", "push"], cwd=netlify_dir, check=True)
# print("✅ GITHUB COMMIT {timestamp}")
