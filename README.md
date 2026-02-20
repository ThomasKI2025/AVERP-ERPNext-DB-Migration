# AVERP → ERPNext Migration Tool

> Vollautomatische Migration von AVERP ERP-Daten nach ERPNext

## 🎯 Quick Start

```bash
# 1. FDB-Datei platzieren
cp /pfad/zur/averp-datenbank.fdb ./averp-database.fdb

# 2. ERPNext Credentials konfigurieren
./setup_credentials.sh

# 3. Komplette Migration starten
./run_migration.sh
```

Fertig! ✅

---

## 📋 Inhaltsverzeichnis

1. [Systemanforderungen](#systemanforderungen)
2. [Installation](#installation)
3. [Konfiguration](#konfiguration)
4. [Migration durchführen](#migration-durchführen)
5. [Was wird importiert](#was-wird-importiert)
6. [Troubleshooting](#troubleshooting)
7. [Fortgeschrittene Nutzung](#fortgeschrittene-nutzung)

---

## 🖥️ Systemanforderungen

- **Betriebssystem:** Ubuntu 24.04 LTS (oder ähnlich)
- **ERPNext:** Version 14+ (mit deutschem Sprachpaket)
- **Python:** 3.12+
- **Speicherplatz:** Min. 5 GB frei
- **Berechtigungen:** sudo-Zugriff erforderlich

**Vorinstallierte Software:**
- Firebird Server (wird automatisch installiert falls fehlend)
- MariaDB/MySQL (via ERPNext)
- Python-Pakete (werden automatisch installiert)

---

## 📥 Installation

### Schritt 1: Repository klonen oder herunterladen

```bash
cd /home/ubuntu
git clone https://github.com/CodeCraftyOwl/AVERP-to-ERPNext-Data-Migration.git
cd AVERP-to-ERPNext-Data-Migration
```

### Schritt 2: Installations-Skript ausführen

```bash
chmod +x install.sh
sudo ./install.sh
```

Das Skript installiert automatisch:
- Firebird Server
- Python-Abhängigkeiten (fdb, pandas, requests, pickle)
- Konfiguriert Berechtigungen

---

## ⚙️ Konfiguration

### 1. AVERP-Datenbank platzieren

Kopieren Sie Ihre AVERP FDB-Datei in das Projektverzeichnis und **benennen Sie sie um**:

```bash
cp /pfad/zur/ihrer-averp-datenbank.fdb ./averp-database.fdb
```

**Wichtig:** 
- ✅ Der Dateiname **muss** `averp-database.fdb` sein
- ✅ Die Datei muss im Hauptverzeichnis des Projekts liegen
- ✅ Pfad: `/home/ubuntu/AVERP-to-ERPNext-Data-Migration/averp-database.fdb`

**Alternative:** FDB-Datei mit anderem Namen verwenden

Falls Sie den Dateinamen nicht ändern möchten, editieren Sie `config.py`:

```python
DB_CONFIG = {
    'dsn': '/home/ubuntu/AVERP-to-ERPNext-Data-Migration/IHR-DATEINAME.fdb',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'WIN1252',
}
```

### 2. ERPNext Credentials einrichten

**Option A: Interaktives Setup (Empfohlen)**

```bash
./setup_credentials.sh
```

Das Skript fragt nach:
- ERPNext URL (z.B. `http://localhost:8000`)
- API Key
- API Secret

Credentials werden in `erpnext_credentials.json` gespeichert.

**Option B: Manuelle Konfiguration**

Erstellen Sie die Datei `erpnext_credentials.json`:

```json
{
  "url": "http://localhost:8000",
  "api_key": "ihr_api_key_hier",
  "api_secret": "ihr_api_secret_hier"
}
```

**API Credentials in ERPNext generieren:**

1. Öffnen Sie ERPNext im Browser
2. Gehen Sie zu: **Einstellungen → Benutzer → [Ihr Benutzer]**
3. Klicken Sie auf **"API-Zugang"**
4. Generieren Sie **API Key** und **API Secret**
5. Kopieren Sie die Werte in `erpnext_credentials.json`

### 3. Verzeichnisstruktur überprüfen

Nach der Konfiguration sollte Ihre Struktur so aussehen:

```
AVERP-to-ERPNext-Data-Migration/
├── averp-database.fdb                  ⬅️ Ihre AVERP-Datenbank
├── erpnext_credentials.json            ⬅️ Ihre ERPNext-Zugangsdaten
├── config.py                           # Datenbank-Konfiguration
├── run_migration.sh                    # Haupt-Migrations-Skript
├── setup_credentials.sh                # Credentials-Setup
├── exporter.py                         # AVERP-Exporter
├── migrate_averp_to_erpnext.py         # Haupt-Pipeline
└── export/                             # Exportierte JSON-Dateien (automatisch erstellt)
```

---

## 🚀 Migration durchführen

### Automatische Komplett-Migration (Empfohlen)

Ein einziger Befehl für alles:

```bash
./run_migration.sh
```

**Was passiert:**
1. ✅ Prüft AVERP-Datenbank (averp-database.fdb)
2. ✅ Exportiert alle Tabellen → `export/*.json`
3. ✅ Validiert JSON-Dateien
4. ✅ Testet ERPNext-Verbindung
5. ✅ Importiert Daten nach ERPNext:
   - Artikel (Items)
   - Kunden (Customers)
   - Werke/Lager (Warehouses)
   - Banken (Banks)

**Dauer:** Ca. 10-15 Minuten (abhängig von Datenmenge)

### Schritt-für-Schritt Migration

Falls Sie die Migration in einzelnen Schritten durchführen möchten:

#### Schritt 1: AVERP-Daten exportieren

```bash
python3 exporter.py
```

Exportiert AVERP-Datenbank → JSON-Dateien in `export/`

#### Schritt 2: JSON-Validierung

```bash
python3 analyze_export.py
```

Prüft alle JSON-Dateien auf Fehler.

#### Schritt 3: ERPNext-Verbindung testen

```bash
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel
```

Testet mit 2.365 Artikeln (empfohlen für ersten Test).

#### Schritt 4: Vollständiger Import

```bash
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden werke banken
```

Importiert alle Datentypen.

### Import-Fortschritt überwachen

Während des Imports sehen Sie live:

```
============================================================
📦 SCHRITT 5: ERPNext Datenimport
============================================================

📦 Importiere: artikel
   [100/2365] ✅ 100 | ⏭️  0 | ❌ 0
   [200/2365] ✅ 200 | ⏭️  0 | ❌ 0
   ...
   
📊 Import abgeschlossen:
   ✅ Erfolgreich: 2365
   ⏭️  Übersprungen: 0
   ❌ Fehler: 0
```

---

## 📦 Was wird importiert

### Standardmäßig importierte Datentypen

| AVERP Tabelle | ERPNext DocType | Anzahl* | Status |
|---------------|-----------------|---------|--------|
| `BSA` | **Item** (Artikel) | 2.365 | ✅ Vollständig |
| `BKUNDE` | **Customer** (Kunden) | 15 | ✅ Vollständig |
| `BWERK` | **Warehouse** (Werke/Lager) | 4.343 | ✅ Vollständig |
| `BSBANK` | **Bank** | 7.261 | ✅ Vollständig |

*Anzahl kann bei Ihrer Datenbank abweichen

### Optional importierbare Datentypen

| AVERP Tabelle | ERPNext DocType | Verfügbar |
|---------------|-----------------|-----------|
| `BRLS` | Purchase Invoice | ✅ |
| `BRLSP` | Purchase Invoice Item | ✅ |
| `BADR` | Address | ⏳ Vorbereitet |
| `BPLZ` | - (Referenzdaten) | ⏳ Optional |

### Field-Mappings (Beispiel Artikel)

```python
AVERP-Feld        → ERPNext-Feld
─────────────────────────────────
MASKENKEY         → item_code
ARTBEZ            → item_name
ARTBEZ2           → description
EKNETTO           → valuation_rate
AKTIV_JN          → disabled
```

**Anpassungen:**
- Deutsche ERPNext-Installation wird automatisch erkannt
- Item Group: `Produkte`
- Stock UOM: `Stk`
- Territory: `Alle Regionen`
- Customer Group: `Alle Kundengruppen`
- Company: `Testfirma` (wird aus ERPNext gelesen)

---

## 🔧 Troubleshooting

### Problem: "FDB-Datei nicht gefunden"

**Fehler:**
```
❌ FDB-Datei nicht gefunden: /home/ubuntu/.../Produktiv-restored.fdb
```

**Lösung:**
```bash
# Prüfen Sie den Pfad
ls -lh Produktiv-restored.fdb

# Falls nicht vorhanden, kopieren Sie die Datei:
cp /ihr/pfad/averp.fdb ./Produktiv-restored.fdb
```

### Problem: "Firebird-Verbindung fehlgeschlagen"

**Fehler:**
```
❌ Fehler: Unable to complete network request to host "localhost"
```

**Lösung:**
```bash
# Firebird-Server starten
sudo systemctl start firebird3.0
sudo systemctl status firebird3.0

# Falls nicht installiert:
sudo apt-get install -y firebird3.0-server
```

### Problem: "ERPNext Verbindung fehlgeschlagen"

**Fehler:**
```
❌ Verbindung fehlgeschlagen: 401 Unauthorized
```

**Lösung:**
1. Prüfen Sie `erpnext_credentials.json`
2. Testen Sie API manuell:
   ```bash
   python3 -c "
   import json, requests
   with open('erpnext_credentials.json') as f:
       creds = json.load(f)
   r = requests.get(f'{creds[\"url\"]}/api/method/frappe.auth.get_logged_user',
                    headers={'Authorization': f'token {creds[\"api_key\"]}:{creds[\"api_secret\"]}'})
   print('Status:', r.status_code, r.text)
   "
   ```

### Problem: "Too many connections"

**Fehler:**
```
❌ pymysql.err.OperationalError: (1040, 'Too many connections')
```

**Lösung:**
```bash
# MariaDB neustarten
sudo systemctl restart mariadb
sleep 3

# Migration erneut starten
./run_migration.sh
```

### Problem: "BrokenPipeError bei API-Import"

**Symptom:** Einige Datentypen (Customer, Warehouse) schlagen bei API-Import fehl

**Lösung:** Das Tool verwendet automatisch **Bench Console Import** für problematische DocTypes.

Falls manuell benötigt:
```bash
./run_all_imports.sh
```

### Problem: "JSON-Validierungsfehler"

**Fehler:**
```
❌ kunden_chunk1.json: Expecting value: line 1080 column 17
```

**Lösung:**
```bash
# Automatische JSON-Reparatur
python3 analyze_export.py --fix

# Oder neu exportieren:
rm -rf export/*.json
python3 exporter.py
```

### Problem: "Could not find Territory: Alle Gebiete"

**Ursache:** ERPNext verwendet andere deutsche Bezeichnungen

**Lösung:** Wird automatisch erkannt! Das Tool liest die korrekten Werte aus Ihrer ERPNext-Installation.

Manuelle Prüfung:
```bash
sudo -u erpnext-user /home/erpnext-user/frappe-bench/env/bin/python -c "
import sys
sys.path.insert(0, '/home/erpnext-user/frappe-bench/apps/frappe')
import os
os.chdir('/home/erpnext-user/frappe-bench/sites')
import frappe
frappe.init(site='mysite.localhost')
frappe.connect()
print('Territories:', frappe.get_all('Territory', pluck='name'))
frappe.destroy()
"
```

---

## 📊 Logs und Fehlerbehandlung

### Log-Dateien

Nach jeder Migration werden Logs erstellt:

```
migration_YYYYMMDD_HHMMSS.log  # Kompletter Ablauf
import_errors_*.json           # Fehlgeschlagene Datensätze
exporter.log                   # AVERP-Export Details
```

### Fehler-Logs anzeigen

```bash
# Letzte Migration
cat migration_*.log | tail -50

# Fehlerhafte Datensätze
cat import_errors_artikel_*.json | jq '.'

# Export-Log
tail -50 exporter.log
```

### Import-Statistik

Nach erfolgreichem Import:

```bash
# Zeige Zusammenfassung
grep "Erfolgreich" migration_*.log
```

Beispiel-Output:
```
✅ Erfolgreich: 2365 (Artikel)
✅ Erfolgreich: 15 (Kunden)
✅ Erfolgreich: 4343 (Werke)
```

---

## 🔍 Fortgeschrittene Nutzung

### Nur bestimmte Datentypen importieren

```bash
# Nur Artikel
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel

# Artikel und Kunden
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden

# Alle wichtigen Typen
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden werke banken
```

### Test-Import (10 Datensätze)

```bash
python3 erpnext_importer.py
# Wähle Option 1: "Artikel importieren (TEST - 10 Datensätze)"
```

### Interaktiver Modus

```bash
python3 migrate_averp_to_erpnext.py --interactive
```

Benutzergeführte Migration mit Abfragen.

### FDB-Datei mit neuem Export

```bash
python3 migrate_averp_to_erpnext.py --fdb ./Produktiv-restored.fdb --data-types artikel kunden
```

Exportiert neu aus FDB und importiert direkt.

### Bench Console Import (für API-Probleme)

Falls die API nicht funktioniert:

```bash
# Import-Skripte generieren
python3 bench_import_all.py

# In Bench Console ausführen
sudo su - erpnext-user
cd ~/frappe-bench
bench console

# Im Console:
exec(open('/tmp/import_customers.py').read())
exec(open('/tmp/import_warehouses.py').read())
exec(open('/tmp/import_banks.py').read())
```

### Field-Mappings anpassen

Editieren Sie `erpnext_importer.py`:

```python
FIELD_MAPPING = {
    'artikel': {
        'doctype': 'Item',
        'fields': {
            'MASKENKEY': 'item_code',
            'ARTBEZ': 'item_name',
            'ARTBEZ2': 'description',
            # Fügen Sie weitere Felder hinzu:
            'IHR_FELD': 'erpnext_feld',
        },
        'defaults': {
            'item_group': 'Produkte',  # An Ihre Installation anpassen
            'stock_uom': 'Stk',
        }
    }
}
```

### Neuen Datentyp hinzufügen

1. **queries.py** - SQL-Query hinzufügen:
```python
QUERIES = {
    'ihr_typ': "SELECT * FROM IHRE_TABELLE",
}
```

2. **erpnext_importer.py** - Field-Mapping hinzufügen:
```python
FIELD_MAPPING['ihr_typ'] = {
    'doctype': 'ERPNext DocType',
    'fields': {...},
    'defaults': {...}
}
```

3. **Exportieren und Importieren:**
```bash
python3 exporter.py
python3 migrate_averp_to_erpnext.py --skip-export --data-types ihr_typ
```

---

## 📋 Checkliste für erfolgreiche Migration

- [ ] Ubuntu 24.04 mit sudo-Zugriff
- [ ] ERPNext installiert und läuft
- [ ] AVERP FDB-Datei kopiert nach `./Produktiv-restored.fdb`
- [ ] `erpnext_credentials.json` erstellt mit gültigen API-Credentials
- [ ] Firebird Server läuft (`sudo systemctl status firebird3.0`)
- [ ] MariaDB läuft (`sudo systemctl status mariadb`)
- [ ] Mindestens 5 GB freier Speicherplatz
- [ ] Test-Import erfolgreich (10 Datensätze)
- [ ] Vollständiger Import ausgeführt
- [ ] Daten in ERPNext UI verifiziert

---

## 🆘 Support

### Bei Problemen

1. **Logs prüfen:** `cat migration_*.log | tail -100`
2. **Verbindung testen:** `python3 migrate_averp_to_erpnext.py --skip-export`
3. **JSON validieren:** `python3 analyze_export.py`

### Häufige Fragen

**Q: Kann ich die Migration mehrfach ausführen?**  
A: Ja! Bereits existierende Datensätze werden automatisch übersprungen.

**Q: Wie lange dauert die Migration?**  
A: Ca. 10-15 Minuten für 2.365 Artikel + 15 Kunden + 4.343 Werke + 7.261 Banken

**Q: Werden Daten in AVERP verändert?**  
A: Nein! AVERP wird nur lesend zugegriffen. Keine Änderungen.

**Q: Was passiert bei Abbruch?**  
A: Bereits importierte Daten bleiben in ERPNext. Beim nächsten Start werden nur fehlende Datensätze importiert.

**Q: Wie kann ich Daten löschen und neu importieren?**  
A: In ERPNext UI die entsprechenden DocTypes löschen, dann Migration erneut starten.

---

## 📝 Lizenz & Credits

**Entwickelt für:** AVERP → ERPNext Migration  
**Version:** 1.0  
**Python:** 3.12+  
**Getestet mit:** ERPNext v14, Ubuntu 24.04 LTS

---

## 🎉 Fertig!

Nach erfolgreicher Migration:

1. **Öffnen Sie ERPNext im Browser**
2. **Prüfen Sie die importierten Daten:**
   - Lager → Artikel (2.365 Items)
   - Verkauf → Kunden (15 Customers)
   - Lager → Lager (4.343 Warehouses)
   - Buchhaltung → Banken (7.261 Banks)

**Viel Erfolg mit ERPNext! 🚀**
