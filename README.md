# camera_data_pickup

Lokálně běžící systém pro **monitoring barev LED diod a malého displeje** pomocí externí USB webkamery. Kamera snímá zařízení (např. relé s diodami), systém automaticky detekuje oblasti zájmu, klasifikuje barvy pomocí natrénovaného ML modelu a loguje jakékoli změny stavu.

## Jak to funguje

1. **Snímání** — USB webkamera snímá obraz zařízení s diodami/displejem.
2. **Detekce ROI** — systém automaticky najde oblasti zájmu (jasné body) přes HSV V-kanál, prahování a kontury — bez ručního zadávání souřadnic.
3. **Klasifikace** — ML klasifikátor (k-NN, trénovaný uživatelem) rozpozná barvu v každé detekované oblasti.
4. **Logování** — změny barev a jejich stav (`ok` / `error`) se zapisují do výstupního logu pro další zpracování.

**Co se sleduje:**
- **Diody** — červená / zelená
- **Displej** — červená / žlutá / zelená

## Struktura

Kód projektu je v adresáři [`Camera_read2/`](Camera_read2/):

| Soubor | Zodpovědnost |
|---|---|
| `capture.py` | Snímání obrazu z kamery |
| `detect.py` | Automatická detekce oblastí zájmu (ROI) |
| `calibrate.py` | Interaktivní kalibrace — přiřazení detekovaných oblastí k zónám |
| `features.py` | Extrakce barevných příznaků (HSV statistiky) |
| `classifier.py` | Trénink a predikce k-NN klasifikátoru |
| `train.py` | Trénink modelu z nasbíraných dat |
| `monitor.py` | Hlavní monitorovací smyčka (statický i dynamický režim) |
| `output.py` | Zápis událostí do logu |
| `main.py` | Vstupní bod aplikace |
| `config.json` | Konfigurace (kamera, detekce, monitoring, zóny, klasifikátor) |

## Instalace

Vyžaduje Python 3.10+.

```bash
cd Camera_read2
pip3 install -r requirements.txt
```

## Použití

```bash
# 1. Kalibrace — přiřazení detekovaných oblastí k zónám
python3 calibrate.py

# 2. Nasbírání trénovacích dat a natrénování modelu
python3 train.py

# 3. Spuštění monitoringu
python3 main.py
```

Veškeré konfigurovatelné hodnoty (index kamery, rozlišení, prahy detekce, interval monitoringu, definice zón) jsou v `config.json`.

## Testy

```bash
cd Camera_read2
python3 -m pytest tests/ -v
```

## Konfigurace zón

Zóny (diody / displeje) se definují v `config.json` — každá má štítky barev, mapování barvy na stav, cestu k modelu a souřadnice ROI. Příklad:

```json
"zones": {
  "diode_1": {
    "labels": ["red", "green"],
    "status_map": { "red": "error", "green": "ok" },
    "model_path": "models/diode_1_knn.joblib",
    "roi": [263, 194, 400, 329]
  }
}
```

## Poznámky

- Natrénované modely (`*.joblib`) a runtime logy (`logs/`) se generují lokálně a nejsou verzované.
- Zelená LED nemusí být dostatečně jasná pro automatickou detekci — kalibraci provádět s rozsvícenou červenou LED (v statickém režimu je ROI fixní a klasifikátor rozliší barvy na stejném místě).
