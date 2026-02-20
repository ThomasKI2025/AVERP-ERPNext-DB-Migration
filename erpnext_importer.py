# erpnext_importer.py
# Importiert exportierte JSON-Daten in ERPNext via REST-API

import os
import json
import requests
from config import EXPORT_PATH

# ERPNext API Konfiguration
import sys

# Konfiguration aus Datei oder Umgebungsvariablen laden
CONFIG_FILE = 'erpnext_credentials.json'

def load_config():
    """Lädt ERPNext Konfiguration"""
    # Versuche aus Datei zu laden
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('url', 'http://localhost:8000'), config.get('api_key'), config.get('api_secret')
    
    # Fallback zu Umgebungsvariablen
    url = os.environ.get('ERPNEXT_URL', 'http://localhost:8000')
    api_key = os.environ.get('ERPNEXT_API_KEY', '')
    api_secret = os.environ.get('ERPNEXT_API_SECRET', '')
    
    return url, api_key, api_secret

ERP_URL, API_KEY, API_SECRET = load_config()

if not API_KEY or not API_SECRET:
    print("\n⚠️  FEHLER: API Credentials nicht konfiguriert!")
    print("\nBitte erstellen Sie 'erpnext_credentials.json' mit:")
    print('{\n  "url": "http://localhost:8000",\n  "api_key": "ihr_api_key",\n  "api_secret": "ihr_api_secret"\n}')
    print("\nOder setzen Sie Umgebungsvariablen:")
    print("export ERPNEXT_URL='http://localhost:8000'")
    print("export ERPNEXT_API_KEY='...'")
    print("export ERPNEXT_API_SECRET='...'")
    sys.exit(1)

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'token {API_KEY}:{API_SECRET}'
}

# Mapping von AvERP zu ERPNext Feldern
FIELD_MAPPING = {
    'kunden': {
        'doctype': 'Customer',
        'fields': {
            'MASKENKEY': 'customer_name',
            'AKTIV_JN': 'disabled'
        },
        'defaults': {
            'customer_type': 'Company',
            'customer_group': 'Alle Kundengruppen',
            'territory': 'Alle Gebiete'
        }
    },
    'artikel': {
        'doctype': 'Item',
        'fields': {
            'MASKENKEY': 'item_code',
            'ARTBEZ': 'item_name',
            'ARTBEZ2': 'description',
            'EKNETTO': 'valuation_rate',
            'AKTIV_JN': 'disabled'
        },
        'defaults': {
            'item_group': 'Produkte',
            'stock_uom': 'Stk',
            'is_stock_item': 1,
            'include_item_in_manufacturing': 0
        }
    },
    'werke': {
        'doctype': 'Warehouse',
        'fields': {
            'MASKENKEY': 'warehouse_name',
            'WERKST': 'warehouse_name',  # Alternative wenn MASKENKEY leer
            'NOTIZ': 'warehouse_name'  # Weitere Alternative
        },
        'defaults': {
            'is_group': 0,
            'company': 'Your Company'  # Muss angepasst werden
        }
    },
    'banken': {
        'doctype': 'Bank',
        'fields': {
            'BANKNAME': 'bank_name',
            'SWIFT': 'swift_number'
        },
        'defaults': {}
    },
    'eingangsrechnungen': {
        'doctype': 'Purchase Invoice',
        'fields': {
            'MASKENKEY': 'name',
            'LIEFDATUM': 'posting_date',
            'BKUNDE_ID_LINKKEY': 'supplier',
        },
        'defaults': {
            'company': 'Your Company',
            'currency': 'EUR'
        }
    },
    'eingangsrechnungspositionen': {
        'doctype': 'Purchase Invoice Item',
        'fields': {
            'BRLS_ID_LSNR': 'parent',
            'BSA_ID_ARTNR': 'item_code',
            'MENGE': 'qty',
        },
        'defaults': {
            'parenttype': 'Purchase Invoice',
            'parentfield': 'items'
        }
    }
}

def transform_data(doctype_key, averp_data):
    """Transformiert AvERP-Daten zu ERPNext-Format"""
    if doctype_key not in FIELD_MAPPING:
        return averp_data
        
    mapping = FIELD_MAPPING[doctype_key]
    transformed = {'doctype': mapping['doctype']}
    
    # Defaults anwenden
    if 'defaults' in mapping:
        transformed.update(mapping['defaults'])
    
    # Feldmappings anwenden
    for averp_field, erpnext_field in mapping['fields'].items():
        if averp_field in averp_data:
            value = averp_data[averp_field]
            
            # Überspringe null/NaN/None Werte
            if value in [None, 'NaN', '', float('nan')]:
                continue
            if isinstance(value, float) and str(value) == 'nan':
                continue
                
            # Spezielle Transformationen
            if averp_field == 'AKTIV_JN':
                value = 0 if value == 'J' else 1  # J=aktiv -> disabled=0
            elif erpnext_field == 'barcode' and value:
                # Barcode in ERPNext erfordert Child-Table Format
                continue  # Wird später separat behandelt
                
            transformed[erpnext_field] = value
    
    return transformed

def test_connection():
    """Testet die Verbindung zu ERPNext"""
    try:
        response = requests.get(
            f"{ERP_URL}/api/method/frappe.auth.get_logged_user",
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            user = response.json().get('message')
            print(f"✅ Verbindung erfolgreich! Angemeldet als: {user}")
            return True
        else:
            print(f"❌ Verbindung fehlgeschlagen: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Verbindungsfehler: {str(e)}")
        return False

def check_exists(doctype, name):
    """Prüft ob ein Dokument bereits existiert"""
    try:
        response = requests.get(
            f"{ERP_URL}/api/resource/{doctype}/{name}",
            headers=HEADERS,
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def import_json_to_erpnext(doctype_key, json_file, limit=None, skip_existing=True):
    """Importiert JSON-Datei zu ERPNext"""
    print(f"\n📦 Importiere {os.path.basename(json_file)}...")
    
    # Lade JSON-Datei mit Fehlerbehandlung
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON-Fehler in {os.path.basename(json_file)}: {e}")
        print(f"   ⏭️  Überspringe diese Datei...")
        return 0, 1, 0
    except Exception as e:
        print(f"   ❌ Fehler beim Laden der Datei: {e}")
        print(f"   ⏭️  Überspringe diese Datei...")
        return 0, 1, 0
    
    if limit:
        data = data[:limit]
        print(f"   Limitiert auf {limit} Datensätze")
    
    success_count = 0
    error_count = 0
    skip_count = 0
    errors = []
    
    for i, entry in enumerate(data, 1):
        try:
            transformed = transform_data(doctype_key, entry)
            doctype = transformed['doctype']
            
            # Bestimme eindeutige ID für Existenzprüfung
            doc_id = None
            if 'item_code' in transformed:
                doc_id = transformed['item_code']
            elif 'customer_name' in transformed:
                doc_id = transformed['customer_name']
            
            # Prüfe ob bereits vorhanden
            if skip_existing and doc_id and check_exists(doctype, doc_id):
                skip_count += 1
                if i % 100 == 0:
                    print(f"   [{i}/{len(data)}] ✅ {success_count} | ⏭️  {skip_count} | ❌ {error_count}")
                continue
            
            response = requests.post(
                f"{ERP_URL}/api/resource/{doctype}",
                headers=HEADERS,
                json=transformed,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                success_count += 1
                if i % 100 == 0:
                    print(f"   [{i}/{len(data)}] ✅ {success_count} | ⏭️  {skip_count} | ❌ {error_count}")
            else:
                error_count += 1
                error_msg = response.text[:200]
                errors.append({
                    'id': entry.get('ID'),
                    'maskenkey': entry.get('MASKENKEY'),
                    'error': error_msg
                })
                if error_count <= 5:  # Zeige nur erste 5 Fehler
                    print(f"   ❌ [{i}] Fehler: {error_msg}")
                
        except Exception as e:
            error_count += 1
            error_msg = str(e)[:200]
            errors.append({
                'id': entry.get('ID'),
                'maskenkey': entry.get('MASKENKEY'),
                'error': error_msg
            })
            if error_count <= 5:
                print(f"   ❌ [{i}] Exception: {error_msg}")
    
    print(f"\n📊 Import abgeschlossen:")
    print(f"   ✅ Erfolgreich: {success_count}")
    print(f"   ⏭️  Übersprungen: {skip_count}")
    print(f"   ❌ Fehler: {error_count}")
    
    # Speichere Fehler-Log
    if errors:
        error_file = f"import_errors_{doctype_key}_{os.path.basename(json_file).replace('.json', '.json')}" 
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)
        print(f"   💾 Fehler-Log: {error_file}")
    
    return success_count, error_count, skip_count

def main():
    """Hauptfunktion - importiert alle verfügbaren Daten"""
    print("="*60)
    print("🚀 AVERP → ERPNext Import Tool")
    print("="*60)
    print(f"ERPNext URL: {ERP_URL}")
    print()
    
    # Teste Verbindung
    if not test_connection():
        print("\n❌ Bitte prüfen Sie Ihre Konfiguration!")
        return
    
    if not os.path.exists(EXPORT_PATH):
        print(f"\n❌ Export-Verzeichnis {EXPORT_PATH} nicht gefunden!")
        return
    
    # Verfügbare Export-Dateien finden
    export_files = {}
    for filename in os.listdir(EXPORT_PATH):
        if filename.endswith('.json') and not filename.endswith('.backup'):
            # Extrahiere Tabellennamen (z.B. 'kunden_chunk1.json' -> 'kunden')
            table_name = filename.split('_chunk')[0]
            if table_name not in export_files:
                export_files[table_name] = []
            export_files[table_name].append(filename)
    
    # Zeige verfügbare Importe
    print("\n📋 Verfügbare Datentypen:")
    for i, table_name in enumerate(sorted(export_files.keys()), 1):
        files = export_files[table_name]
        mapped = "✅" if table_name in FIELD_MAPPING else "⚠️"
        print(f"   {i:2d}. {mapped} {table_name:20s} ({len(files)} Datei(en))")
    
    print("\n" + "="*60)
    print("Optionen:")
    print("="*60)
    print("1. Artikel importieren (TEST - 10 Datensätze)")
    print("2. Artikel importieren (VOLLSTÄNDIG)")
    print("3. Kunden importieren (wenn verfügbar)")
    print("4. Alle gemappten Datentypen importieren")
    print("0. Beenden")
    print()
    
    choice = input("Ihre Wahl: ").strip()
    
    if choice == '1':
        # TEST-Import Artikel
        file_path = os.path.join(EXPORT_PATH, 'artikel_chunk1.json')
        if os.path.exists(file_path):
            import_json_to_erpnext('artikel', file_path, limit=10)
        else:
            print("❌ artikel_chunk1.json nicht gefunden!")
    
    elif choice == '2':
        # Vollständiger Import Artikel
        file_path = os.path.join(EXPORT_PATH, 'artikel_chunk1.json')
        if os.path.exists(file_path):
            confirm = input("\n⚠️  Import von allen Artikeln starten? (ja/nein): ")
            if confirm.lower() in ['ja', 'j', 'yes', 'y']:
                import_json_to_erpnext('artikel', file_path)
        else:
            print("❌ artikel_chunk1.json nicht gefunden!")
    
    elif choice == '3':
        # Kunden import
        file_path = os.path.join(EXPORT_PATH, 'kunden_chunk1.json')
        if os.path.exists(file_path):
            limit = input("Anzahl Datensätze (oder Enter für alle): ").strip()
            limit = int(limit) if limit.isdigit() else None
            import_json_to_erpnext('kunden', file_path, limit=limit)
        else:
            print("❌ kunden_chunk1.json nicht gefunden!")
    
    elif choice == '4':
        # Alle gemappten Typen
        confirm = input("\n⚠️  Alle gemappten Datentypen importieren? (ja/nein): ")
        if confirm.lower() in ['ja', 'j', 'yes', 'y']:
            for table_name in FIELD_MAPPING.keys():
                if table_name in export_files:
                    for file in sorted(export_files[table_name]):
                        file_path = os.path.join(EXPORT_PATH, file)
                        import_json_to_erpnext(table_name, file_path)
    
    elif choice == '0':
        print("Auf Wiedersehen!")
    
    else:
        print("❌ Ungültige Auswahl")

if __name__ == "__main__":
    main()
