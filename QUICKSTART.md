# Quick Reference - AVERP → ERPNext Migration

## 🚀 Schnellstart (3 Schritte)

```bash
# 1. FDB-Datei platzieren
cp /pfad/zur/averp.fdb ./averp-database.fdb

# 2. Credentials
./setup_credentials.sh

# 3. Migration
./run_migration.sh
```

## 📁 Wichtige Dateien

| Datei | Zweck | Erforderlich |
|-------|-------|--------------|
| `averp-database.fdb` | AVERP-Datenbank | ✅ Ja |
| `erpnext_credentials.json` | ERPNext API-Zugang | ✅ Ja |
| `config.py` | Datenbank-Config | ⚙️ Optional |

## 🔧 Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `./install.sh` | Installiert alle Abhängigkeiten |
| `./setup_credentials.sh` | ERPNext API konfigurieren |
| `./run_migration.sh` | **Vollständige Migration** |
| `python3 exporter.py` | Nur AVERP exportieren |
| `python3 analyze_export.py` | JSON-Dateien validieren |

## 📊 Was wird importiert

- ✅ **2.365 Artikel** (Items)
- ✅ **15 Kunden** (Customers)  
- ✅ **4.343 Werke** (Warehouses)
- ✅ **7.261 Banken** (Banks)

## 🐛 Troubleshooting

| Problem | Lösung |
|---------|---------|
| FDB nicht gefunden | `ls averp-database.fdb` prüfen |
| Firebird nicht läuft | `sudo systemctl start firebird3.0` |
| API-Fehler 401 | Credentials in `erpnext_credentials.json` prüfen |
| Too many connections | `sudo systemctl restart mariadb` |

## 📝 Log-Dateien

```bash
# Letzte Migration
cat migration_*.log | tail -50

# Fehler anzeigen  
cat import_errors_*.json | jq '.'
```

## 🔄 Re-Import

Bereits importierte Daten werden übersprungen!

```bash
# Einfach erneut ausführen:
./run_migration.sh
```

## ⚙️ Erweitert

```bash
# Nur bestimmte Typen
python3 migrate_averp_to_erpnext.py --skip-export --data-types artikel kunden

# Interaktiv
python3 migrate_averp_to_erpnext.py --interactive

# Test (10 Datensätze)
python3 erpnext_importer.py  # Option 1
```

## 📞 Support

1. **Logs prüfen:** `cat migration_*.log`
2. **README lesen:** `cat README.md`
3. **Verbindung testen:** `python3 migrate_averp_to_erpnext.py --skip-export`
