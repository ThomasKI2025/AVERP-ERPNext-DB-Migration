# manual_export.py  
# Manueller Export für inkompatible Firebird-Versionen

import os
import csv
import json
from config import EXPORT_PATH

def create_sample_data():
    """Erstellt Beispieldaten für Tests"""
    sample_data = {
        'kunden': [
            {'id': 1, 'name': 'Musterkunde', 'ort': 'Musterstadt'},
            {'id': 2, 'name': 'Beispiel GmbH', 'ort': 'Beispielstadt'}
        ],
        'artikel': [
            {'id': 1, 'bezeichnung': 'Beispielartikel', 'preis': 100.00},
            {'id': 2, 'bezeichnung': 'Testartikel', 'preis': 250.50}
        ]
    }
    
    if not os.path.exists(EXPORT_PATH):
        os.makedirs(EXPORT_PATH)
    
    for table_name, data in sample_data.items():
        # JSON Export
        json_file = os.path.join(EXPORT_PATH, f"{table_name}_chunk1.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # CSV Export (für ERPNext Import)
        csv_file = os.path.join(EXPORT_PATH, f"{table_name}.csv")
        if data:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        print(f"Erstellt: {json_file} und {csv_file}")

def convert_sql_dump_to_json(sql_file):
    """Konvertiert SQL-Dumps zu JSON (falls verfügbar)"""
    # Implementierung für SQL-Dump-Parsing
    print("SQL-Dump-Konvertierung noch nicht implementiert")

if __name__ == "__main__":
    print("Erstelle Beispieldaten für Import-Tests...")
    create_sample_data()
    print("\nHinweis: Für echte Daten aus AvERP benötigen wir:")
    print("1. Eine kompatible Firebird-Version")
    print("2. Oder SQL-Dumps der Tabellen")
    print("3. Oder Export der Daten auf dem ursprünglichen System")