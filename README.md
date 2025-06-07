# AKT Mamut Expeditions

Automatyczny system do generowania interaktywnych map ekspedycji na stronie [https://aktmamut.eu](https://aktmamut.eu), oparty na danych z Google Sheets i ścieżkach GPX.

---

## ✨ Funkcjonalności

* 📅 Pobieranie danych o wyprawach z Google Sheets (dystans, czas, przewyższenia, linki itp.)
* 🛸 Łączenie i upraszczanie ścieżek GPX do formatu GeoJSON
* 🌈 Automatyczne przypisywanie kolorów trasom na podstawie bliskości (tak, by się nie nakładały)
* 📊 Generowanie `EXPEDITIONS.html` z mapą i trasami
* 📃 Kopiowanie wynikowych plików do odpowiednich katalogów (Netlify / GitHub Pages)
* 📦 Automatyczne commitowanie i publikacja na GitHubie

---

## 📚 Struktura katalogów

```
C:\github\Expeditions\
├── all_generate_script.py          # Główny skrypt uruchamiający cały pipeline
├── gpx01_merge_gpx_to_geojson.py  # Scalanie plików GPX w jeden GeoJSON
├── gpx02_simplify_geojson.py      # Uproszczenie danych
├── gpx03_assign_colors.py         # Przypisanie kolorów trasom
├── html01_generate_expeditions.py # Generowanie pliku HTML z mapą
├── gpx\                           # Surowe GPX-y
├── output\                        # GeoJSON-y po obóbce (merged, simplified, colored)
├── archive\                       # Archiwum starych wyników
```

Plik HTML i GeoJSON są kopiowane do:

```
C:\github\aktmamut.eu\maps\EXPEDITIONS.html
C:\github\aktmamut.eu\gpx\colored.geojson
```

---

## ⚡ Jak uruchomić

1. Upewnij się, że masz plik `.env` z kluczem do Google Sheets API:

```
GOOGLE_API_KEY=Twój_klucz_API
```

2. Zainstaluj wymagane biblioteki:

```bash
pip install -r requirements.txt
```

3. Uruchom wszystko:

```bash
python all_generate_script.py
```

---

## 💚 Zależności (requirements.txt)

```txt
geopandas
pandas
folium
shapely
requests
networkx
python-dotenv
```

---

## 🌐 Wersja online

Wynikowy plik `EXPEDITIONS.html` jest publikowany automatycznie w:

```
https://aktmamut.eu/maps/EXPEDITIONS.html
```

Trasy GPX (uproszczone, z kolorami) są w:

```
https://aktmamut.eu/gpx/colored.geojson
```

---

## 🚀 Planowane usprawnienia

* ✅ Automatyczne sprawdzanie, czy nowe GPX-y zostały dodane
* ✅ Eksport listy zdobytych szczytów (np. "Korona Gór Polski")
* ✅ Edytor danych z poziomu przeglądarki

---

## 📲 Kontakt

Prowadzi: **AKT Mamut**
Mapa, kod i dane: [https://github.com/aktmamut.eu](https://github.com/aktmamut.eu)
