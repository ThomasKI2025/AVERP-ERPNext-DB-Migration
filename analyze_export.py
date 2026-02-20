# analyze_export.py
# Analysiert die exportierten Daten für das ERPNext Mapping

import os
import json
from config import EXPORT_PATH

def analyze_json_structure(json_file):
    """Analysiert die Struktur einer JSON-Datei"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        return {}
    
    # Erste Zeile analysieren
    sample = data[0]
    field_info = {}
    
    for field, value in sample.items():
        field_info[field] = {
            'type': type(value).__name__,
            'sample_value': str(value)[:50] if value is not None else None
        }
    
    return {
        'total_records': len(data),
        'fields': field_info
    }

def main():
    print("=== ANALYSE DER EXPORTIERTEN DATEN ===\n")
    
    for filename in sorted(os.listdir(EXPORT_PATH)):
        if filename.endswith('.json'):
            file_path = os.path.join(EXPORT_PATH, filename)
            print(f"📄 {filename}")
            
            try:
                analysis = analyze_json_structure(file_path)
                print(f"   Datensätze: {analysis['total_records']:,}")
                print(f"   Felder ({len(analysis['fields'])}):")
                
                for field, info in list(analysis['fields'].items())[:10]:  # Erste 10
                    print(f"     {field}: {info['type']} = {info['sample_value']}")
                
                if len(analysis['fields']) > 10:
                    print(f"     ... und {len(analysis['fields'])-10} weitere Felder")
                    
            except Exception as e:
                print(f"   FEHLER: {e}")
            
            print()

if __name__ == "__main__":
    main()