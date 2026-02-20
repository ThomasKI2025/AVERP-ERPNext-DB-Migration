# 🚀 AVERP → ERPNext Migration - Quick Start

## Status: ✅ Pipeline vollständig implementiert

### Bereits importiert:
- ✅ **2.365 Artikel** (Items) → ERPNext

### Bereit zum Import:
- ⏭️ **5 Kunden** (Customers)
- ⏭️ **4.343 Werke** (Warehouses)
- ⏭️ **7.261 Banken** (Banks)
- ⏭️ **10 Eingangsrechnungen** + 23 Positionen

---

## 🎯 Komplette Pipeline ausführen

### Schnellstart (mit vorhandenen JSON-Dateien)

```bash
cd /home/ubuntu/AVERP-to-ERPNext-Data-Migration

# Alle wichtigen Datentypen importieren
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden werke banken
```

### Interaktiver Modus

```bash
python3 migrate_averp_to_erpnext.py --interactive
```

### Von FDB-Datei (wenn Sie eine neue AVERP-Datenbank haben)

```bash
python3 migrate_averp_to_erpnext.py --fdb /pfad/zur/averp.fdb --data-types artikel kunden
```

---

## 📋 Was macht die Pipeline?

1. **Schritt 1:** Prüft AVERP FDB-Datei (optional)
2. **Schritt 2:** Exportiert Daten aus AVERP → JSON (optional)
3. **Schritt 3:** Validiert alle JSON-Dateien
4. **Schritt 4:** Testet ERPNext API-Verbindung
5. **Schritt 5:** Importiert Daten nach ERPNext

---

## 📦 Einzelne Schritte

### 1. Export aus AVERP (wenn neue FDB-Datei vorhanden)

```bash
# Config anpassen
nano config.py  # FDB-Pfad eintragen

# Export ausführen
python3 exporter.py
```

### 2. Import nach ERPNext

**Mit Pipeline-Tool:**
```bash
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden werke
```

**Oder manuell mit Menü:**
```bash
python3 erpnext_importer.py
```

---

## 🔧 Wichtige Dateien

| Datei | Zweck |
|-------|-------|
| `migrate_averp_to_erpnext.py` | **Hauptskript** - Komplette Pipeline |
| `exporter.py` | Export aus AVERP FDB → JSON |
| `erpnext_importer.py` | Import JSON → ERPNext |
| `config.py` | AVERP Datenbank-Konfiguration |
| `erpnext_credentials.json` | ERPNext API-Zugangsdaten |
| `MIGRATION_GUIDE.md` | Detaillierte Dokumentation |

---

## ⚙️ Konfiguration anpassen

### ERPNext Credentials (falls noch nicht vorhanden)

```bash
./setup_credentials.sh
```

### Field-Mappings anpassen

Editiere `erpnext_importer.py`, Sektion `FIELD_MAPPING`:

```python
FIELD_MAPPING = {
    'artikel': {
        'doctype': 'Item',
        'fields': {
            'MASKENKEY': 'item_code',
            'ARTBEZ': 'item_name',
            # Weitere Felder hinzufügen...
        },
        'defaults': {
            'item_group': 'Produkte',  # An Ihre Installation anpassen
            'stock_uom': 'Stk',
        }
    }
}
```

---

## 📊 Verfügbare Daten

```bash
# Übersicht über alle Daten
python3 -c "
import json, os
for f in sorted(os.listdir('export')):
    if f.endswith('.json'):
        with open(f'export/{f}') as file:
            data = json.load(file)
            print(f'{len(data):6d} - {f}')
"
```

Ausgabe:
- 2.365 Artikel
- 5 Kunden (teilweise korrupte Originaldatei)
- 4.343 Werke/Standorte
- 7.261 Banken
- 10 Eingangsrechnungen
- 23 Rechnungspositionen
- 58.622 Postleitzahlen (optional)
- 80.133 Feld-Definitionen (Metadaten)

---

## 🐛 Bekannte Probleme & Lösungen

### Problem: BrokenPipeError bei Customer/Supplier Import

Die ERPNext API hat manchmal Probleme mit bestimmten DocTypes.

**Lösung:** Verwende bench console für diese Typen:

```bash
# 1. Erstelle Import-Skript
python3 bench_import.py

# 2. Führe in bench console aus
sudo su - erpnext-user
cd ~/frappe-bench
bench console

# 3. Im Console:
exec(open('/tmp/import_items.py').read())
```

### Problem: "Item Group 'All Item Groups' not found"

ERPNext ist in Deutsch installiert.

**Lösung:** Automatisch gelöst - Pipeline verwendet deutsche Werte:
- `item_group: 'Produkte'`
- `stock_uom: 'Stk'`

---

## ✅ Checkliste für vollständige Migration

- [x] AVERP Daten exportiert (JSON-Dateien vorhanden)
- [x] ERPNext Credentials konfiguriert
- [x] Verbindung zu ERPNext getestet
- [x] 2.365 Artikel importiert ✅
- [ ] 5 Kunden importieren
- [ ] 4.343 Werke importieren
- [ ] 7.261 Banken importieren
- [ ] 10 Eingangsrechnungen importieren
- [ ] Daten in ERPNext UI überprüfen

---

## 🚀 Nächste Schritte

1. **Kunden importieren:**
   ```bash
   python3 migrate_averp_to_erpnext.py --skip-export --data-types kunden
   ```

2. **Werke importieren (für Lagerverwaltung):**
   ```bash
   python3 migrate_averp_to_erpnext.py --skip-export --data-types werke
   ```

3. **Alles auf einmal:**
   ```bash
   python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden werke banken eingangsrechnungen
   ```

---

## 📝 Logs prüfen

```bash
# Letzte Migration
cat migration_*.log | tail -50

# Import-Fehler Details
cat import_errors_*.json
```

---

## 📞 Bei Fragen

1. Siehe `MIGRATION_GUIDE.md` für Details
2. Prüfe Log-Dateien
3. Teste ERPNext Verbindung: `python3 erpnext_importer.py`
