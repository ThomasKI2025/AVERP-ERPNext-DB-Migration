#!/bin/bash
# run_migration.sh
# Vollautomatische AVERP → ERPNext Migration

set -e  # Beende bei Fehler

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   🚀 AVERP → ERPNext Vollautomatische Migration         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log-Datei
LOGFILE="migration_$(date +%Y%m%d_%H%M%S).log"

# Funktion für farbige Ausgabe und Logging
log() {
    echo -e "$1" | tee -a "$LOGFILE"
}

log_success() {
    log "${GREEN}✅ $1${NC}"
}

log_error() {
    log "${RED}❌ $1${NC}"
}

log_warning() {
    log "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    log "${BLUE}ℹ️  $1${NC}"
}

# ============================================================
# SCHRITT 1: Voraussetzungen prüfen
# ============================================================

log ""
log "════════════════════════════════════════════════════════════"
log "  SCHRITT 1/5: Systemvoraussetzungen prüfen"
log "════════════════════════════════════════════════════════════"
log ""

# Prüfe Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    log_success "Python gefunden: $PYTHON_VERSION"
else
    log_error "Python 3 nicht gefunden!"
    exit 1
fi

# Prüfe FDB-Datei
if [ -f "Produktiv-restored.fdb" ]; then
    FDB_SIZE=$(du -h Produktiv-restored.fdb | awk '{print $1}')
    log_success "AVERP FDB-Datei gefunden: $FDB_SIZE"
else
    log_error "AVERP FDB-Datei nicht gefunden!"
    log_info "Bitte kopieren Sie Ihre AVERP-Datenbank nach:"
    log_info "  ./Produktiv-restored.fdb"
    log_info ""
    log_info "Befehl: cp /pfad/zur/averp.fdb ./Produktiv-restored.fdb"
    exit 1
fi

# Prüfe ERPNext Credentials
if [ -f "erpnext_credentials.json" ]; then
    log_success "ERPNext Credentials gefunden"
else
    log_error "ERPNext Credentials nicht gefunden!"
    log_info "Bitte führen Sie aus: ./setup_credentials.sh"
    exit 1
fi

# Prüfe Firebird
if systemctl is-active --quiet firebird3.0 2>/dev/null; then
    log_success "Firebird Server läuft"
elif command -v fbguard &> /dev/null; then
    log_warning "Firebird installiert aber nicht gestartet"
    log_info "Starte Firebird..."
    sudo systemctl start firebird3.0
    sleep 2
    log_success "Firebird gestartet"
else
    log_warning "Firebird nicht installiert"
    log_info "Installiere Firebird Server..."
    sudo apt-get update > /dev/null 2>&1
    sudo apt-get install -y firebird3.0-server firebird3.0-utils > /dev/null 2>&1
    sudo systemctl start firebird3.0
    sleep 2
    log_success "Firebird installiert und gestartet"
fi

# Prüfe Python-Pakete
log_info "Prüfe Python-Abhängigkeiten..."
MISSING_PACKAGES=""

for package in fdb pandas requests pickle5; do
    if ! python3 -c "import ${package%%[*}" 2>/dev/null; then
        MISSING_PACKAGES="$MISSING_PACKAGES $package"
    fi
done

if [ -n "$MISSING_PACKAGES" ]; then
    log_warning "Fehlende Pakete:$MISSING_PACKAGES"
    log_info "Installiere fehlende Pakete..."
    pip3 install $MISSING_PACKAGES --break-system-packages --quiet
    log_success "Pakete installiert"
else
    log_success "Alle Python-Pakete vorhanden"
fi

# ============================================================
# SCHRITT 2: AVERP-Daten exportieren
# ============================================================

log ""
log "════════════════════════════════════════════════════════════"
log "  SCHRITT 2/5: AVERP-Daten exportieren"
log "════════════════════════════════════════════════════════════"
log ""

log_info "Exportiere Daten aus AVERP FDB..."
log_info "Dies kann einige Minuten dauern..."
log ""

if python3 exporter.py >> "$LOGFILE" 2>&1; then
    log_success "Export abgeschlossen"
    
    # Zähle exportierte Dateien
    EXPORT_COUNT=$(ls -1 export/*.json 2>/dev/null | wc -l)
    log_info "Exportierte Dateien: $EXPORT_COUNT"
else
    log_error "Export fehlgeschlagen!"
    log_info "Siehe Log: $LOGFILE"
    exit 1
fi

# ============================================================
# SCHRITT 3: JSON-Dateien validieren
# ============================================================

log ""
log "════════════════════════════════════════════════════════════"
log "  SCHRITT 3/5: Exportierte Daten validieren"
log "════════════════════════════════════════════════════════════"
log ""

log_info "Validiere JSON-Dateien..."
log ""

python3 << 'PYEOF'
import json
import os

export_path = './export'
files_ok = 0
files_error = 0

important_files = ['artikel_chunk1.json', 'kunden_chunk1.json', 'werke_chunk1.json', 'banken_chunk1.json']

for filename in sorted(os.listdir(export_path)):
    if filename.endswith('.json'):
        filepath = os.path.join(export_path, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            is_important = filename in important_files
            marker = "📌" if is_important else "  "
            print(f"{marker} ✅ {filename:45s} - {len(data):6d} Datensätze")
            files_ok += 1
        except Exception as e:
            print(f"  ❌ {filename:45s} - FEHLER: {str(e)[:40]}")
            files_error += 1

print()
print(f"Validierung: {files_ok} OK, {files_error} Fehler")

if files_error > 0:
    exit(1)
PYEOF

if [ $? -eq 0 ]; then
    log_success "Alle JSON-Dateien gültig"
else
    log_error "JSON-Validierung fehlgeschlagen!"
    exit 1
fi

# ============================================================
# SCHRITT 4: ERPNext-Verbindung testen
# ============================================================

log ""
log "════════════════════════════════════════════════════════════"
log "  SCHRITT 4/5: ERPNext-Verbindung testen"
log "════════════════════════════════════════════════════════════"
log ""

log_info "Teste Verbindung zu ERPNext..."

python3 << 'PYEOF'
import json
import requests
import sys

try:
    with open('erpnext_credentials.json', 'r') as f:
        creds = json.load(f)
    
    url = creds['url']
    headers = {
        'Authorization': f"token {creds['api_key']}:{creds['api_secret']}"
    }
    
    response = requests.get(
        f"{url}/api/method/frappe.auth.get_logged_user",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        user = response.json().get('message')
        print(f"✅ Verbindung erfolgreich!")
        print(f"   URL: {url}")
        print(f"   Benutzer: {user}")
    else:
        print(f"❌ Verbindung fehlgeschlagen: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Fehler: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    log_error "ERPNext-Verbindung fehlgeschlagen!"
    log_info "Prüfen Sie erpnext_credentials.json"
    exit 1
fi

# ============================================================
# SCHRITT 5: Daten nach ERPNext importieren
# ============================================================

log ""
log "════════════════════════════════════════════════════════════"
log "  SCHRITT 5/5: Daten nach ERPNext importieren"
log "════════════════════════════════════════════════════════════"
log ""

log_warning "Dies kann 10-15 Minuten dauern..."
log_info "Importiere: Artikel, Kunden, Werke, Banken"
log ""

# Bereite Pickle-Daten vor
log_info "Bereite Daten vor..."
python3 << 'PYEOF'
import json
import pickle
import os

for name, json_file in [
    ('kunden', 'export/kunden_chunk1.json'),
    ('werke', 'export/werke_chunk1.json'),
    ('banken', 'export/banken_chunk1.json')
]:
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        with open(f'/tmp/{name}_data.pkl', 'wb') as f:
            pickle.dump(data, f)
        print(f"✅ {name}: {len(data)} Datensätze vorbereitet")
PYEOF

log ""
log_info "Starte Import..."
log ""

# Führe Import aus
if ./run_all_imports.sh 2>&1 | tee -a "$LOGFILE"; then
    log ""
    log_success "Import abgeschlossen!"
else
    log_error "Import mit Fehlern abgeschlossen"
    log_info "Details siehe: $LOGFILE"
fi

# ============================================================
# ZUSAMMENFASSUNG
# ============================================================

log ""
log "════════════════════════════════════════════════════════════"
log "  ✅ MIGRATION ABGESCHLOSSEN"
log "════════════════════════════════════════════════════════════"
log ""

# Zeige Zusammenfassung aus Log
if [ -f "$LOGFILE" ]; then
    log_info "Zusammenfassung:"
    log ""
    
    grep -E "(Erfolgreich|Übersprungen|Fehler):" "$LOGFILE" | tail -20 | while read line; do
        log "  $line"
    done
fi

log ""
log_info "📊 Vollständiger Log: $LOGFILE"
log ""
log_success "Sie können jetzt Ihre Daten in ERPNext prüfen!"
log_info "  • Lager → Artikel"
log_info "  • Verkauf → Kunden"
log_info "  • Lager → Lager (Warehouses)"
log_info "  • Buchhaltung → Banken"
log ""
log "════════════════════════════════════════════════════════════"
log ""
