#!/bin/bash
# install.sh
# Installiert alle Abhängigkeiten für AVERP → ERPNext Migration

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   📦 AVERP → ERPNext Migration - Installation          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Prüfe sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Bitte als root ausführen: sudo ./install.sh"
    exit 1
fi

echo "Installiere System-Abhängigkeiten..."
echo ""

# Update Package List
echo "📦 Aktualisiere Paketliste..."
apt-get update -qq

# Installiere Firebird
echo "📦 Installiere Firebird Server..."
apt-get install -y firebird3.0-server firebird3.0-utils -qq
systemctl enable firebird3.0
systemctl start firebird3.0

# Installiere Python-Pakete
echo "📦 Installiere Python-Abhängigkeiten..."
pip3 install --break-system-packages --quiet \
    fdb \
    pandas \
    requests \
    pickle5

echo ""
echo "✅ Installation abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "  1. FDB-Datei platzieren: cp /pfad/zur/averp.fdb ./averp-database.fdb"
echo "  2. Credentials einrichten: ./setup_credentials.sh"
echo "  3. Migration starten: ./run_migration.sh"
echo ""
