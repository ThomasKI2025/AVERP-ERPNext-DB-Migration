#!/bin/bash
# Setup-Skript für ERPNext API Credentials

echo "============================================================"
echo "🔧 ERPNext API Credentials Setup"
echo "============================================================"
echo ""

# Prüfe ob Datei bereits existiert
if [ -f "erpnext_credentials.json" ]; then
    echo "⚠️  erpnext_credentials.json existiert bereits!"
    echo ""
    read -p "Möchten Sie sie überschreiben? (ja/nein): " overwrite
    if [ "$overwrite" != "ja" ] && [ "$overwrite" != "j" ]; then
        echo "Abgebrochen."
        exit 0
    fi
fi

# ERPNext URL
echo ""
echo "📍 Schritt 1: ERPNext URL"
echo "   Beispiele:"
echo "   - http://localhost:8000"
echo "   - http://192.168.1.100:8000"
echo "   - https://ihr-erp.example.com"
echo ""
read -p "ERPNext URL [http://localhost:8000]: " erpnext_url
erpnext_url=${erpnext_url:-http://localhost:8000}

# API Key
echo ""
echo "🔑 Schritt 2: API Key"
echo "   (Gehen Sie zu ERPNext → Benutzerprofil → API Access → Generate Keys)"
echo ""
read -p "API Key: " api_key

# API Secret
echo ""
echo "🔐 Schritt 3: API Secret"
echo ""
read -s -p "API Secret: " api_secret
echo ""

# Validierung
if [ -z "$api_key" ] || [ -z "$api_secret" ]; then
    echo ""
    echo "❌ API Key und Secret dürfen nicht leer sein!"
    exit 1
fi

# JSON-Datei erstellen
echo ""
echo "💾 Erstelle erpnext_credentials.json..."

cat > erpnext_credentials.json << EOF
{
  "url": "$erpnext_url",
  "api_key": "$api_key",
  "api_secret": "$api_secret"
}
EOF

chmod 600 erpnext_credentials.json

echo "✅ Credentials gespeichert!"
echo ""

# Verbindung testen
echo "🔍 Teste Verbindung zu ERPNext..."
echo ""

response=$(curl -s -w "\n%{http_code}" -X GET "${erpnext_url}/api/method/frappe.auth.get_logged_user" \
    -H "Authorization: token ${api_key}:${api_secret}" 2>&1)

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✅ Verbindung erfolgreich!"
    echo "   Angemeldet als: $(echo $body | grep -o '"message":"[^"]*"' | cut -d'"' -f4)"
    echo ""
    echo "============================================================"
    echo "🎉 Setup abgeschlossen!"
    echo "============================================================"
    echo ""
    echo "Sie können jetzt den Import starten mit:"
    echo "   python3 erpnext_importer.py"
    echo ""
else
    echo "❌ Verbindung fehlgeschlagen!"
    echo "   HTTP Status: $http_code"
    echo "   Response: $body"
    echo ""
    echo "Bitte prüfen Sie:"
    echo "   - Ist ERPNext unter $erpnext_url erreichbar?"
    echo "   - Sind die API Credentials korrekt?"
    echo "   - Hat der Benutzer die erforderlichen Rechte?"
    echo ""
    echo "Die Credentials wurden trotzdem gespeichert."
    echo "Sie können sie manuell bearbeiten:"
    echo "   nano erpnext_credentials.json"
fi
