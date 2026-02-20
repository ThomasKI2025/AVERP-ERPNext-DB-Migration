# Dateien-Übersicht

## 📁 Hauptverzeichnis

```
AVERP-to-ERPNext-Data-Migration/
├── 📖 README.md                          ← Vollständige Dokumentation
├── 📋 QUICKSTART.md                      ← Schnellreferenz
├── 📄 DATEIEN.md                         ← Diese Datei
│
├── 🔧 Konfiguration
│   ├── config.py                         ← Firebird-Datenbankzugriff
│   ├── erpnext_config.py                 ← ERPNext-spezifische Einstellungen
│   └── erpnext_credentials.json          ← API-Zugangsdaten (zu erstellen)
│
├── 🚀 Ausführbare Skripte
│   ├── install.sh                        ← Installiert Abhängigkeiten
│   ├── setup_credentials.sh              ← Interaktives Credentials-Setup
│   ├── run_migration.sh                  ← Haupt-Migrations-Skript (START HIER!)
│   └── run_all_imports.sh                ← Import-Ausführung (bench console)
│
├── 🐍 Python-Module
│   ├── exporter.py                       ← AVERP FDB → JSON Export
│   ├── erpnext_importer.py               ← JSON → ERPNext API Import
│   ├── migrate_averp_to_erpnext.py       ← Haupt-Pipeline-Skript
│   ├── bench_import.py                   ← Artikel-Import (bench console)
│   ├── bench_import_all.py               ← Alle Typen (bench console)
│   ├── queries.py                        ← SQL-Queries für AVERP-Tabellen
│   ├── utils.py                          ← Hilfsfunktionen
│   ├── analyze_export.py                 ← JSON-Validierung
│   ├── db_inspector.py                   ← Datenbank-Inspektor
│   ├── csv_converter.py                  ← JSON → CSV Konverter
│   └── test_import_pipeline.py           ← Test-Skript
│
├── 📊 Daten (zu erstellen/generiert)
│   ├── averp-database.fdb                ← AVERP-Datenbank (SIE MÜSSEN DIESE DATEI HIERHER KOPIEREN!)
│   ├── export/                           ← Exportierte JSON-Dateien
│   │   ├── artikel_chunk1.json
│   │   ├── kunden_chunk1.json
│   │   ├── werke_chunk1.json
│   │   ├── banken_chunk1.json
│   │   └── ...
│   ├── csv_export/                       ← Optional: CSV-Exporte
│   └── migration_*.log                   ← Migrations-Logs
│
├── 📚 Dokumentation
│   ├── MIGRATION_GUIDE.md                ← Detaillierte Migrations-Anleitung
│   ├── erpnext_import_analysis.md        ← ERPNext-Analyse
│   ├── projekt_beschreibung.md           ← Projektbeschreibung
│   ├── fb25_export_guide.md              ← Firebird 2.5 Export-Guide
│   └── IMPORT_ANLEITUNG.md               ← Import-Anleitung
│
└── 🗂️ Zusätzlich
    ├── frappe-erpnext/                   ← ERPNext Source (falls geklont)
    ├── averp_export_env/                 ← Python Virtual Environment
    └── __pycache__/                      ← Python Cache
```

## 🎯 Welche Dateien sind wichtig?

### ✅ Für Anwender (Sie!)

| Datei | Zweck | Aktion |
|-------|-------|--------|
| **README.md** | Vollständige Anleitung | Lesen |
| **QUICKSTART.md** | Schnellreferenz | Lesen |
| **install.sh** | Installation | `sudo ./install.sh` |
| **setup_credentials.sh** | API-Setup | `./setup_credentials.sh` |
| **run_migration.sh** | **Migration starten** | `./run_migration.sh` |
| **averp-database.fdb** | AVERP-Datenbank | **SIE MÜSSEN DIESE DATEI ERSTELLEN!** |
| **erpnext_credentials.json** | API-Zugangsdaten | Wird von setup_credentials.sh erstellt |

### 🔧 Für Entwickler

| Datei | Zweck |
|-------|-------|
| `config.py` | Datenbank-Konfiguration anpassen |
| `erpnext_importer.py` | Field-Mappings bearbeiten |
| `queries.py` | SQL-Queries für neue Tabellen |
| `bench_import_all.py` | Neue Import-Skripte generieren |

## 📝 Logs und Outputs

Nach der Migration finden Sie:

```
migration_20260211_120658.log          ← Vollständiger Migrations-Log
import_errors_artikel_*.json           ← Fehlerhafte Artikel-Datensätze
import_errors_kunden_*.json            ← Fehlerhafte Kunden-Datensätze
exporter.log                           ← AVERP-Export-Details
```

## 🚫 Nicht benötigt

Diese Dateien können ignoriert werden:
- `__pycache__/` - Python Cache
- `averp_export_env/` - Virtual Environment
- `frappe-erpnext/` - ERPNext Source (nur für Entwicklung)
- `*.pyc` - Kompilierte Python-Dateien

## 📂 export/ Verzeichnis

Nach dem Export finden Sie hier:

```
export/
├── artikel_chunk1.json                 (2.365 Datensätze)
├── kunden_chunk1.json                  (15 Datensätze)
├── werke_chunk1.json                   (4.343 Datensätze)
├── banken_chunk1.json                  (7.261 Datensätze)
├── eingangsrechnungen_chunk1.json      (10 Datensätze)
├── eingangsrechnungspositionen_chunk1.json (23 Datensätze)
├── postleitzahlen_chunk*.json          (58.622 Datensätze, 6 Dateien)
├── felder_chunk*.json                  (80.133 Datensätze, 9 Dateien)
└── tabellen_chunk1.json                (6.538 Datensätze)
```

## 🎯 Arbeitsablauf

1. **Installation:** `sudo ./install.sh`
2. **FDB kopieren:** `cp /pfad/averp.fdb ./averp-database.fdb`
3. **Credentials:** `./setup_credentials.sh`
4. **Migration:** `./run_migration.sh`
5. **Logs prüfen:** `cat migration_*.log`
6. **ERPNext öffnen:** Daten überprüfen

## 💡 Tipps

- **Backup:** Erstellen Sie ein ERPNext-Backup vor dem Import!
- **Logs:** Alle Logs bleiben erhalten für spätere Analyse
- **Re-Import:** Bereits importierte Daten werden übersprungen
- **Parallel:** Sie können ERPNext während des Imports nutzen

## 🆘 Hilfe

1. Lesen Sie **README.md** für Details
2. Prüfen Sie **migration_*.log** bei Problemen
3. Nutzen Sie **QUICKSTART.md** für schnelle Befehle
