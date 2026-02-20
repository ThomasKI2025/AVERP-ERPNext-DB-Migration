# AVERP → ERPNext Migration Guide

## 📋 Übersicht

Komplette Migrationspipeline von AVERP ERP System zu ERPNext.

```
AVERP FDB-Datei → JSON Export → ERPNext Import
```

## 🚀 Quick Start

### Option 1: Mit vorhandenen JSON-Dateien (empfohlen)

Wenn Sie bereits JSON-Dateien im `export/` Verzeichnis haben:

```bash
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden werke
```

### Option 2: Komplette Migration von FDB-Datei

```bash
python3 migrate_averp_to_erpnext.py --fdb /pfad/zur/averp.fdb --data-types artikel kunden werke
```

### Option 3: Interaktiver Modus

```bash
python3 migrate_averp_to_erpnext.py --interactive
```

## 📦 Pipeline-Schritte

### Schritt 1: AVERP Datenbank Export

**Manuell:**
```bash
# Config anpassen
nano config.py  # FDB-Pfad eintragen

# Export ausführen
python3 exporter.py
```

**Automatisch:**
```bash
python3 migrate_averp_to_erpnext.py --fdb /pfad/zur/averp.fdb
```

### Schritt 2: JSON-Validierung

Prüfe exportierte Dateien:
```bash
python3 analyze_export.py
```

### Schritt 3: ERPNext Credentials

Falls noch nicht konfiguriert:
```bash
./setup_credentials.sh
```

Oder manuell `erpnext_credentials.json` erstellen:
```json
{
  "url": "http://localhost:8000",
  "api_key": "ihr_api_key",
  "api_secret": "ihr_api_secret"
}
```

### Schritt 4: Import nach ERPNext

**Einzelne Datentypen:**
```bash
# Nur Artikel
python3 erpnext_importer.py  # Wähle Option 2

# Nur Kunden  
python3 erpnext_importer.py  # Wähle Option 3
```

**Komplette Migration:**
```bash
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden werke banken eingangsrechnungen
```

## 📊 Unterstützte Datentypen

| AVERP Tabelle | Datensätze | ERPNext DocType | Status | Priorität |
|---------------|------------|-----------------|--------|-----------|
| `BSA` (Artikel) | 2.365 | Item | ✅ Implementiert | Hoch |
| `BKUNDE` (Kunden) | 5 | Customer | ✅ Implementiert | Hoch |
| `BWERK` (Werke) | 4.343 | Warehouse | ✅ Vorbereitet | Hoch |
| `BSBANK` (Banken) | 7.261 | Bank | ✅ Vorbereitet | Mittel |
| `BRLS` (Eingangsrechnungen) | 10 | Purchase Invoice | ✅ Vorbereitet | Mittel |
| `BRLSP` (Rechnungspositionen) | 23 | Purchase Invoice Item | ✅ Vorbereitet | Mittel |
| `BPLZ` (PLZ) | 58.622 | - | ⏸️ Optional | Niedrig |
| `A_FELDER` | 80.133 | - | ⏸️ Metadaten | Niedrig |

## 🔧 Konfiguration

### config.py

```python
DB_CONFIG = {
    'dsn': '/pfad/zur/averp.fdb',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'WIN1252',
}

EXPORT_PATH = './export/'
CHUNK_SIZE = 10000
```

### erpnext_importer.py - Field Mappings

Anpassen der Feldmappings:

```python
FIELD_MAPPING = {
    'artikel': {
        'doctype': 'Item',
        'fields': {
            'MASKENKEY': 'item_code',
            'ARTBEZ': 'item_name',
            # ...
        },
        'defaults': {
            'item_group': 'Produkte',  # Anpassen an Ihre ERPNext Installation
            'stock_uom': 'Stk',
        }
    }
}
```

## 🐛 Troubleshooting

### Problem: API BrokenPipeError

**Symptom:** `BrokenPipeError: [Errno 32] Broken pipe` bei Customer/Supplier Import

**Lösung:** Verwende bench console für diese DocTypes:

```bash
sudo su - erpnext-user
cd ~/frappe-bench
bench console

# Im Console:
exec(open('/tmp/import_customers.py').read())
```

### Problem: Deutsche ERPNext Felder nicht gefunden

**Symptom:** `Item Group 'All Item Groups' not found`

**Lösung:** Prüfe deutsche Feldnamen:

```python
# In bench console
frappe.get_all("Item Group", pluck="name")
frappe.get_all("UOM", pluck="name")
```

Aktualisiere in `erpnext_importer.py`:
```python
'defaults': {
    'item_group': 'Produkte',  # Nicht 'All Item Groups'
    'stock_uom': 'Stk',        # Nicht 'Nos'
}
```

### Problem: JSON-Validierungsfehler

**Symptom:** `json.JSONDecodeError` beim Import

**Lösung:** Repariere JSON-Dateien:

```bash
python3 analyze_export.py  # Findet fehlerhafte Dateien
```

Manuell reparieren oder neu exportieren.

## 📈 Import-Statistiken

Nach erfolgreichem Import:

```bash
# Log-Datei prüfen
cat migration_*.log

# Fehler-Details
cat import_errors_*.json
```

## 🔄 Re-Import / Update

Vorhandene Datensätze werden automatisch übersprungen. Für Update:

```python
# In erpnext_importer.py
import_json_to_erpnext('artikel', file_path, skip_existing=False)
```

## 📝 Logs

- `migration_YYYYMMDD_HHMMSS.log` - Komplette Pipeline
- `import_errors_DATATYPE_*.json` - Import-Fehler Details
- `exporter.log` - Export-Prozess

## 🎯 Empfohlene Reihenfolge

1. **Artikel** (Item) - Basis für alle anderen
2. **Kunden** (Customer) - Für Verkaufsdokumente
3. **Werke** (Warehouse) - Für Lagerverwaltung
4. **Banken** (Bank) - Für Zahlungen
5. **Eingangsrechnungen** (Purchase Invoice) - Historische Daten

## ⚙️ Erweiterte Optionen

### Nur bestimmte Anzahl Datensätze testen

```python
# In Python
import erpnext_importer
erpnext_importer.import_json_to_erpnext('artikel', 'export/artikel_chunk1.json', limit=10)
```

### Custom Field Mapping hinzufügen

Editiere `erpnext_importer.py` und füge hinzu:

```python
FIELD_MAPPING['neuer_typ'] = {
    'doctype': 'DocType Name',
    'fields': {
        'AVERP_FELD': 'erpnext_feld',
    },
    'defaults': {
        'standard_feld': 'standard_wert'
    }
}
```

## 📞 Support

Bei Problemen:
1. Log-Dateien prüfen
2. JSON-Dateien validieren
3. ERPNext Verbindung testen
4. Field-Mappings auf deutsche Lokalisierung prüfen

## ✅ Checkliste

- [ ] AVERP FDB-Datei vorhanden oder JSON-Export durchgeführt
- [ ] `erpnext_credentials.json` konfiguriert
- [ ] ERPNext Verbindungstest erfolgreich
- [ ] Deutsche Feldnamen in ERPNext überprüft
- [ ] Test-Import mit 10 Datensätzen durchgeführt
- [ ] Vollständiger Import gestartet
- [ ] Import-Logs überprüft
- [ ] Daten in ERPNext UI verifiziert
