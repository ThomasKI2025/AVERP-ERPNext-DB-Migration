# csv_converter.py
# Konvertiert AvERP JSON-Exporte zu ERPNext-kompatiblen CSV-Dateien

import os
import json
import csv
import pandas as pd
from config import EXPORT_PATH

# ERPNext CSV-Templates (Standard-Felder)
ERPNEXT_TEMPLATES = {
    'Customer': {
        'required_fields': ['Customer Name'],
        'fields': [
            'Customer Name', 'Customer Type', 'Customer Group', 'Territory',
            'Gender', 'Date of Birth', 'Phone', 'Mobile No', 'Email Id',
            'Website', 'Address Line 1', 'Address Line 2', 'City', 'County',
            'State', 'Country', 'Pincode', 'Fax', 'Tax ID', 'Disabled'
        ]
    },
    'Item': {
        'required_fields': ['Item Code', 'Item Name', 'Item Group'],
        'fields': [
            'Item Code', 'Item Name', 'Item Group', 'Default Unit of Measure',
            'Stock UOM', 'Disabled', 'Allow Alternative Item', 'Is Stock Item',
            'Include Item In Manufacturing', 'Opening Stock', 'Valuation Rate',
            'Standard Rate', 'Is Purchase Item', 'Is Sales Item', 'Description'
        ]
    },
    'Address': {
        'required_fields': ['Address Title', 'Address Type'],
        'fields': [
            'Address Title', 'Address Type', 'Address Line 1', 'Address Line 2',
            'City', 'County', 'State', 'Country', 'Pincode', 'Phone', 'Fax',
            'Email Id', 'Is Primary Address', 'Is Shipping Address'
        ]
    }
}

# Mapping AvERP → ERPNext
FIELD_MAPPINGS = {
    'kunden': {
        'target_doctype': 'Customer',
        'mappings': {
            'ID': 'Customer Name',
            'MASKENKEY': None,  # Ignore
            'EIG_LIEFNR': None,
            'BADR_ID_ADRNR': None,  # Wird separat behandelt
            'AKTIV_JN': {'target': 'Disabled', 'transform': lambda x: '0' if x == 'J' else '1'},
            'ERFDATUM': None,
            'KRELIMIT': None
        },
        'defaults': {
            'Customer Type': 'Company',
            'Customer Group': 'All Customer Groups', 
            'Territory': 'All Territories',
            'Country': 'Austria'
        }
    },
    'artikel': {
        'target_doctype': 'Item',
        'mappings': {
            'ID': 'Item Code',
            'ARTBEZ': 'Item Name',
            'ARTBEZ2': 'Description',
            'BESTELLEN': {'target': 'Is Purchase Item', 'transform': lambda x: '1' if x == 'J' else '0'},
            'AKTIV_JN': {'target': 'Disabled', 'transform': lambda x: '0' if x == 'J' else '1'}
        },
        'defaults': {
            'Item Group': 'All Item Groups',
            'Default Unit of Measure': 'Nos',
            'Stock UOM': 'Nos',
            'Is Stock Item': '1',
            'Include Item In Manufacturing': '0'
        }
    }
}

def convert_json_to_csv(json_file, output_dir='./csv_export/'):
    """Konvertiert JSON-Export zu ERPNext CSV"""
    
    # Output-Verzeichnis erstellen
    os.makedirs(output_dir, exist_ok=True)
    
    # Dateiname analysieren (z.B. 'kunden_chunk1.json')
    base_name = os.path.basename(json_file).replace('.json', '')
    table_name = base_name.split('_chunk')[0]
    
    if table_name not in FIELD_MAPPINGS:
        print(f"⚠️  Kein Mapping für Tabelle '{table_name}' definiert")
        return None
    
    mapping_config = FIELD_MAPPINGS[table_name]
    target_doctype = mapping_config['target_doctype']
    template = ERPNEXT_TEMPLATES[target_doctype]
    
    print(f"🔄 Konvertiere {json_file} → {target_doctype}")
    
    # JSON-Daten laden (robust)
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content.endswith(']'):
                # Repariere unvollständige JSON-Dateien
                content = content.rstrip(',\n ') + ']'
            data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ JSON-Fehler in {json_file}: {e}")
        return None
    
    # CSV-Daten vorbereiten
    csv_data = []
    
    for record in data:
        csv_row = {}
        
        # Standard-Defaults setzen
        for field, default_value in mapping_config.get('defaults', {}).items():
            csv_row[field] = default_value
        
        # Feldmappings anwenden
        for source_field, mapping_rule in mapping_config['mappings'].items():
            if source_field in record:
                value = record[source_field]
                
                if mapping_rule is None:
                    continue  # Feld ignorieren
                elif isinstance(mapping_rule, dict):
                    # Transformations-Regel
                    target_field = mapping_rule['target']
                    transform_func = mapping_rule.get('transform')
                    if transform_func:
                        value = transform_func(value)
                    csv_row[target_field] = value
                else:
                    # Direktes Mapping
                    csv_row[mapping_rule] = value
        
        # Erforderliche Felder prüfen
        valid_row = True
        for required_field in template['required_fields']:
            if required_field not in csv_row or not csv_row[required_field]:
                print(f"⚠️  Erforderliches Feld '{required_field}' fehlt in Datensatz: {record.get('ID', '?')}")
                valid_row = False
        
        if valid_row:
            csv_data.append(csv_row)
    
    # CSV-Datei schreiben
    if csv_data:
        output_file = os.path.join(output_dir, f"{target_doctype}_{base_name}.csv")
        
        # Alle Template-Felder als Spalten verwenden
        fieldnames = template['fields']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"✅ Exportiert: {output_file} ({len(csv_data)} Datensätze)")
        return output_file
    else:
        print(f"❌ Keine gültigen Daten zum Exportieren gefunden")
        return None

def validate_csv_export(csv_file):
    """Validiert die CSV-Datei gegen ERPNext-Standards"""
    print(f"🔍 Validiere {csv_file}")
    
    try:
        df = pd.read_csv(csv_file)
        
        # Basis-Validierungen
        print(f"   📊 {len(df)} Datensätze gefunden")
        print(f"   📋 {len(df.columns)} Spalten: {list(df.columns)}")
        
        # Erforderliche Felder prüfen (abhängig vom Doctype)
        doctype = os.path.basename(csv_file).split('_')[0]
        if doctype in ERPNEXT_TEMPLATES:
            template = ERPNEXT_TEMPLATES[doctype]
            missing_required = []
            
            for required_field in template['required_fields']:
                if required_field not in df.columns:
                    missing_required.append(required_field)
                elif df[required_field].isnull().any():
                    empty_count = df[required_field].isnull().sum()
                    print(f"   ⚠️  '{required_field}': {empty_count} leere Werte")
            
            if missing_required:
                print(f"   ❌ Fehlende erforderliche Felder: {missing_required}")
                return False
            else:
                print(f"   ✅ Alle erforderlichen Felder vorhanden")
                return True
    
    except Exception as e:
        print(f"   ❌ Validierungsfehler: {e}")
        return False

def main():
    """Konvertiert alle JSON-Dateien zu CSV"""
    print("🚀 AvERP → ERPNext CSV Konverter")
    print("=" * 50)
    
    converted_files = []
    
    # Alle JSON-Dateien im Export-Verzeichnis verarbeiten
    for filename in os.listdir(EXPORT_PATH):
        if filename.endswith('.json'):
            json_file = os.path.join(EXPORT_PATH, filename)
            csv_file = convert_json_to_csv(json_file)
            
            if csv_file:
                converted_files.append(csv_file)
                validate_csv_export(csv_file)
    
    print("\n" + "=" * 50)
    print(f"✅ Konvertierung abgeschlossen: {len(converted_files)} CSV-Dateien erstellt")
    
    if converted_files:
        print("\n📋 NÄCHSTE SCHRITTE:")
        print("1. CSV-Dateien in ERPNext Data Import Tool laden")
        print("2. Template-Mapping überprüfen")  
        print("3. Test-Import mit 5-10 Datensätzen")
        print("4. Bei Erfolg: Vollständigen Import durchführen")

if __name__ == "__main__":
    main()