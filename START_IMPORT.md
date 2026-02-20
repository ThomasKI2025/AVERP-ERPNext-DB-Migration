# 🚀 Schnellstart: AVERP nach ERPNext Import

## Status der Daten

✅ **Bereit zum Import:**
- **2.365 Artikel** (artikel_chunk1.json)
- **7.261 Banken** (banken_chunk1.json)
- **10 Eingangsrechnungen** + 23 Positionen
- **80.133 Felder-Daten** (9 Dateien)
- **58.622 Postleitzahlen** (6 Dateien)
- **6.538 Tabellen** (tabellen_chunk1.json)
- **4.343 Werke** (werke_chunk1.json)

⚠️ **Problem:**
- **Kunden** (kunden_chunk1.json) - JSON-Datei hat Fehler

## Schritt 1: ERPNext API-Credentials einrichten

### 1.1 API Keys in ERPNext generieren

1. Öffnen Sie ERPNext im Browser
2. Klicken Sie auf Ihr **Benutzerprofil** (oben rechts)
3. Gehen Sie zu **API Access**
4. Klicken Sie auf **Generate Keys**
5. Kopieren Sie beide Keys:
   - **API Key**
   - **API Secret** ⚠️ (wird nur einmal angezeigt!)

### 1.2 Credentials-Datei erstellen

```bash
cd /home/ubuntu/AVERP-to-ERPNext-Data-Migration

# Erstelle Konfigurationsdatei aus Vorlage
cp erpnext_credentials.json.example erpnext_credentials.json

# Bearbeite die Datei
nano erpnext_credentials.json
```

Fügen Sie Ihre echten Credentials ein:
```json
{
  "url": "http://localhost:8000",
  "api_key": "9a8b7c6d5e4f3g2h",
  "api_secret": "1a2b3c4d5e6f7g8h"
}
```

Speichern Sie die Datei (Strg+O, Enter, Strg+X).

## Schritt 2: Import starten

### 2.1 TEST-Import (empfohlen!)

```bash
# Aktiviere virtuelle Umgebung (falls vorhanden)
source averp_export_env/bin/activate

# Starte Import-Tool
python3 erpnext_importer.py
```

### 2.2 Im Menü:

```
Wählen Sie Option 1: Artikel importieren (TEST - 10 Datensätze)
```

Dies importiert nur 10 Artikel zum Testen.

### 2.3 In ERPNext überprüfen:

1. Gehen Sie zu **Stock → Item**
2. Prüfen Sie, ob die Artikel korrekt angelegt wurden
3. Überprüfen Sie die Feldmappings

### 2.4 Vollständiger Import:

Wenn der Test erfolgreich war:
```
Starten Sie erneut: python3 erpnext_importer.py
Wählen Sie Option 2: Artikel importieren (VOLLSTÄNDIG)
```

## Schritt 3: Anpassungen vornehmen

Falls Sie Fehler sehen wie:
- **"Item Group 'Products' not found"**
- **"Territory 'All Territories' not found"**

### Lösung:

Bearbeiten Sie `erpnext_importer.py` und passen Sie die Defaults an:

```python
# Zeile ~50-54 - Artikel Defaults
'defaults': {
    'item_group': 'Products',          # ← Ändern Sie dies zu Ihrer Item Group
    'stock_uom': 'Nos',
    'is_stock_item': 1
}

# Zeile ~39-43 - Kunden Defaults
'defaults': {
    'customer_type': 'Company',        # ← Anpassen falls nötig
    'customer_group': 'Commercial',    # ← Anpassen falls nötig  
    'territory': 'All Territories'     # ← Anpassen falls nötig
}
```

### Verfügbare Werte finden:

**In ERPNext:**
- **Item Groups:** Stock → Item Group
- **Customer Groups:** Selling → Setup → Customer Group
- **Territories:** Selling → Setup → Territory

## Schritt 4: Fehlerbehandlung

### Fehler-Logs:

Das Skript erstellt automatisch Fehler-Logs:
```bash
ls -l import_errors_*.json
```

### Fehler analysieren:

```bash
cat import_errors_artikel_chunk1.json | jq '.[0:5]'  # Erste 5 Fehler anzeigen
```

### Häufige Probleme:

1. **"Duplicate entry"** → Datensatz existiert bereits (wird automatisch übersprungen)
2. **"Mandatory field missing"** → Pflichtfeld fehlt im Mapping
3. **"Link validation failed"** → Referenziertes Dokument existiert nicht

## Schritt 5: Weitere Datentypen

Das Projekt enthält Mappings für:
- ✅ **Artikel** (komplett gemappt)
- ⚠️ **Kunden** (JSON-Datei reparieren)

Weitere Typen können hinzugefügt werden in [erpnext_importer.py](erpnext_importer.py):
- Banken
- Eingangsrechnungen
- etc.

## Erweiterte Optionen

### Umgebungsvariablen verwenden (statt Datei):

```bash
export ERPNEXT_URL="http://localhost:8000"
export ERPNEXT_API_KEY="ihr_api_key"
export ERPNEXT_API_SECRET="ihr_api_secret"

python3 erpnext_importer.py
```

### Nur bestimmte Anzahl importieren:

Im Code können Sie das `limit` Parameter ändern.

## Backup!

⚠️ **WICHTIG**: Erstellen Sie vor dem Import ein Backup!

```bash
# Falls Sie Zugriff auf die Bench haben:
cd /path/to/frappe-bench
bench backup

# Oder über ERPNext UI:
# Setup → Download Backups
```

## Hilfe bei Problemen

### Verbindung testen:

```bash
curl -X GET "http://localhost:8000/api/method/frappe.auth.get_logged_user" \
  -H "Authorization: token IHR_API_KEY:IHR_API_SECRET"
```

### Python-Abhängigkeiten:

```bash
pip3 install requests
```

### Logs prüfen:

```bash
# ERPNext Logs
tail -f /path/to/frappe-bench/logs/frappe.log

# Import Fehler-Logs
ls -lh import_errors_*.json
```

---

**Status**: Sie können **sofort mit dem Artikel-Import beginnen**! 

Die Kunden-Datei kann später repariert/neu-exportiert werden.
