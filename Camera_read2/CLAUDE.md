# CLAUDE.md

Tento soubor poskytuje pokyny pro Claude Code (claude.ai/code) při práci s kódem v tomto repozitáři.

**POVINNÉ: Přečti celý tento soubor PŘED jakoukoliv prací na kódu.**

## Hlavní pravidlo — Changelog

Každá instance Clauda MUSÍ po provedení významné změny (nová funkce, refaktoring, změna architektury, oprava bugu) zapsat záznam do sekce Changelog níže. Drobné kosmetické změny (překlepy, formátování) se nezapisují.

Formát záznamu:
```
### [DATUM] — Stručný popis změny
- Co bylo změněno/přidáno
- Důvod změny
- Dotčené soubory
```

## O projektu

Lokálně běžící systém pro monitoring barev LED diod a malého displeje pomocí externí USB webkamery.

**Co sledujeme:**
- **Diody** — svítí červeně nebo zeleně
- **Displej** — svítí červeně, žlutě nebo zeleně

**Jak to funguje:**
1. Kamera snímá obraz relé s diodami/displejem
2. Systém **automaticky detekuje** oblasti zájmu (ROI) — kde jsou diody a displej (žádné ruční zadávání souřadnic)
3. ML klasifikátor (trénovaný uživatelem) rozpoznává barvy v detekovaných oblastech
4. Systém loguje změny barev a jejich stav

**Klíčový rozdíl oproti předchozí verzi (Camera_read):**
- Automatická detekce ROI místo ručního zadávání souřadnic (předchozí verze nefungovala kvůli problémům s ruční konfigurací)

## Status report

**Fáze projektu:** Detekce otestována s kamerou, kalibrace je další krok

**Na čem jsme zaséklí:** Zatím nic

**Důležité — kalibrace diod:**
- Zelená LED není dostatečně jasná pro automatickou detekci (brightness threshold 200)
- Kalibraci (`python3 calibrate.py`) provádět s **červenou LED rozsvícenou**
- V static mode to nevadí — ROI je fixní, klasifikátor rozliší red/green na stejném místě

**Další kroky:**
- Provést kalibraci s červenou LED (`python3 calibrate.py`)
- Nasbírat trénovací data a natrénovat modely
- Spustit monitoring

## Styl kódu — ZÁVAZNÉ pro všechny instance

Aby byl kód konzistentní napříč všemi instancemi Clauda, dodržuj tyto konvence:

**Jazyk:**
- Kód (proměnné, funkce, třídy, komentáře v kódu): **angličtina**
- Komunikace s uživatelem: **čeština**

**Python styl:**
- Python 3.10+
- Žádné type hinty kromě návratových typů funkcí
- Žádné docstringy — kód má být čitelný sám o sobě
- Komentáře jen tam, kde logika není zřejmá
- Pojmenování: `snake_case` pro funkce a proměnné, `PascalCase` pro třídy
- Žádné zbytečné abstrakce — jednoduchý, přímočarý kód
- Konfigurovatelné hodnoty patří do config souboru, ne hardcodované v kódu

**Struktura:**
- Každý soubor = jedna zodpovědnost
- Flat struktura (bez vnořených balíčků), pokud není dobrý důvod
- Použij `python3` a `pip3` (ne `python` nebo `pip`)

**Při změnách:**
- Neměň názvy existujících funkcí/tříd bez důvodu
- Nepřidávej funkce nad rámec toho, co bylo požadováno
- Než něco přepíšeš, přečti si existující kód

## ⚠️ POVINNÉ TESTOVÁNÍ — EXTRÉMNĚ DŮLEŽITÉ ⚠️

Každá instance Clauda MUSÍ při každé změně kódu dodržet tento postup:

1. **PŘED implementací** — napsat/upravit test pro danou funkci v `tests/`
2. **Spustit testy** — `python3 -m pytest tests/ -v` a ověřit že procházejí
3. **Implementovat změnu** v produkčním kódu
4. **Spustit testy ZNOVU** — ověřit že nic není rozbité
5. **Commit + posunout tag** `latest-working` (viz Git checkpointy)

Spouštění testů:
```
python3 -m pytest tests/ -v              # všechny testy
python3 -m pytest tests/test_features.py  # jeden soubor
```

**NIKDY necommituj kód který neprojde testy.**

## Git checkpointy

Projekt používá git tagy jako záchranné body:

- **`foundation`** — trvalý základní kámen. NIKDY se nepřesouvá bez výslovného souhlasu uživatele.
- **`latest-working`** — nejnovější ověřeně funkční verze. Posunuje se po každé úspěšné změně.

**Po každé úspěšně otestované změně:**
```
git add <změněné soubory>
git commit -m "popis změny"
git tag -f latest-working
```

**Návrat k funkční verzi:** `git checkout latest-working`
**Návrat k základu:** `git checkout foundation`

---

## Changelog

### 2026-04-04 — Inicializace projektu
- Vytvořen CLAUDE.md
- Prázdný projekt, začínáme novou implementaci kamerového monitoringu
- Předchozí verze (Camera_read) nefungovala, nový přístup bude definován

### 2026-04-05 — Kompletní implementace všech modulů
- Vytvořeny všechny soubory: capture.py, detect.py, calibrate.py, features.py, classifier.py, train.py, monitor.py, output.py, main.py
- config.json s parametry detekce, monitoringu a klasifikátoru
- requirements.txt se závislostmi
- Klíčová novinka: detect.py — automatická detekce ROI přes jasné body (HSV V-kanál, threshold, kontury)
- calibrate.py — interaktivní kalibrace kde uživatel přiřazuje detekované oblasti k zónám
- monitor.py — podporuje statický i dynamický režim detekce
- Dotčené soubory: všechny (nový projekt)

### 2026-04-05 — Opravy bugů a vylepšení robustnosti
- calibrate.py: oprava přepisování zón — auto-číslování (diode_1, diode_2) umožňuje více zón stejného typu
- train.py: vytvoření training_data/ adresáře pokud neexistuje
- monitor.py: zotavení z chyby kamery (retry s limitem 5 pokusů), srozumitelná chyba při chybějícím modelu
- classifier.py: predict vrací Python str místo numpy string
- Všechny __main__ bloky: ošetření chybějícího/poškozeného config.json
- capture.py, detect.py: přesun import json do __main__ bloku (kde se skutečně používá)
- Dotčené soubory: calibrate.py, train.py, monitor.py, classifier.py, capture.py, detect.py, main.py

### 2026-04-07 — Git checkpointy + test soubory
- Inicializován git repo s tagy `foundation` a `latest-working`
- Vytvořeny test soubory: tests/test_features.py, test_detect.py, test_classifier.py, test_output.py (25 testů, všechny procházejí)
- Přidáno POVINNÉ pravidlo testování do CLAUDE.md — každá změna musí být otestována
- Přidán .gitignore, pytest do requirements.txt
- Dotčené soubory: CLAUDE.md, .gitignore, requirements.txt, tests/
