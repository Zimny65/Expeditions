
# 🌍 AKT Mamut Expeditions 3.0

Zintegrowany system do generowania interaktywnej mapy ekspedycji na stronie:  
👉 https://aktmamut.eu/maps/EXPEDITIONS.html

---

## ✨ Najważniejsze funkcje

- ✅ Automatyczny import danych z arkusza Google Sheets (trasa, data, uczestnicy, dystans, czas, itd.)
- 🧭 Konwersja plików GPX do GeoJSON z pełnymi metadanymi
- 🧪 Upraszczanie śladów tras (mniej punktów – szybsze ładowanie)
- 🌈 Inteligentne przypisywanie kolorów, aby trasy się nie nakładały
- 🗺️ Generowanie interaktywnej mapy (`EXPEDITIONS.html`) z popupami i punktami startowymi
- 🚀 Kopiowanie gotowego pliku GeoJSON do katalogu Netlify (`/maps`)

---

## 📁 Struktura katalogu

```
C:\github\Expeditions\
├── all_generate_script.py         # Jeden skrypt uruchamiający całość (GPX -> HTML)
├── html_generate_expeditions.py  # Oddzielny generator mapy HTML z punktami
├── html_dynamic_trail_layer.js   # Skrypt do dynamicznego ładowania tras na zoom>=10
├── .env                          # Klucz dostępu do Google API
├── gpx\                          # Surowe pliki GPX
├── geojson\                      # Dane pośrednie (merged, simplified, final)
├── output\                       # Gotowe GeoJSON dla mapy HTML
└── archive\                      # (opcjonalnie) kopie archiwalne
```

---

## ⚙️ Wymagania

- Python 3.9+
- Plik `.env` z nazwą arkusza Google i danymi uwierzytelniającymi:

```
GOOGLE_SHEET_NAME=AKT Mamut Expeditions
SHEET_TAB_NAME=ALL
GOOGLE_CREDENTIALS_FILE=credentials.json
```

---

## 🔧 Instalacja zależności

```bash
pip install -r requirements.txt
```

---

## 🚀 Jak uruchomić?

1. Uruchom cały pipeline:

```bash
python all_generate_script.py
```

Wygeneruje i skopiuje `expeditions.geojson` do `C:/github/aktmamut.eu/maps`.

2. (Opcjonalnie) Wygeneruj mapę HTML:

```bash
python html_generate_expeditions.py
```

Wygeneruje `EXPEDITIONS.html` i doda JS do dynamicznego ładowania tras.

---

## 🌐 Hosting

- **Mapa HTML**: [https://aktmamut.eu/maps/EXPEDITIONS.html](https://aktmamut.eu/maps/EXPEDITIONS.html)
- **Trasy GeoJSON**: [https://aktmamut.eu/maps/expeditions.geojson](https://aktmamut.eu/maps/expeditions.geojson)

---

## 📌 TODO

- [ ] Automatyczne commitowanie i deploy na GitHub Pages
- [ ] Historia zmian tras
- [ ] Wyszukiwarka tras i filtracja po górach / kraju / uczestniku

---

## 👣 Autorzy

Projekt prowadzony przez **AKT Mamut**  
Repozytorium: https://github.com/aktmamut.eu
