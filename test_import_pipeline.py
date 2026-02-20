# test_import_pipeline.py
# Vollständige Test- und Validierungspipeline für ERPNext Import

import os
import json
import pandas as pd
from csv_converter import convert_json_to_csv, validate_csv_export

def create_test_sample(csv_file, sample_size=5):
    """Erstellt eine kleine Test-Datei für sicheren Import-Test"""
    
    df = pd.read_csv(csv_file)
    test_df = df.head(sample_size).copy()
    
    # Test-Suffix zu Item Codes hinzufügen um Konflikte zu vermeiden
    if 'Item Code' in test_df.columns:
        test_df['Item Code'] = 'TEST_' + test_df['Item Code'].astype(str)
    if 'Customer Name' in test_df.columns:
        test_df['Customer Name'] = 'TEST_' + test_df['Customer Name'].astype(str)
    
    test_file = csv_file.replace('.csv', '_TEST.csv')
    test_df.to_csv(test_file, index=False)
    
    print(f"📋 Test-Datei erstellt: {test_file} ({sample_size} Datensätze)")
    return test_file

def generate_import_instructions(csv_files):
    """Generiert detaillierte Import-Anweisungen für ERPNext"""
    
    instructions = """
# 🚀 ERPNext Import-Anleitung

## VORBEREITUNG:
1. ERPNext öffnen → Setup → Data Import and Settings → Data Import
2. Zuerst mit TEST-Dateien (5 Datensätze) beginnen!

## IMPORT-REIHENFOLGE (WICHTIG!):
"""
    
    import_order = ['Customer', 'Item', 'Address']  # Abhängigkeiten beachten
    
    for i, doctype in enumerate(import_order, 1):
        matching_files = [f for f in csv_files if doctype in f]
        if matching_files:
            instructions += f"\n{i}. **{doctype}**\n"
            for file in matching_files:
                test_file = file.replace('.csv', '_TEST.csv')
                instructions += f"   - Test: {test_file}\n"
                instructions += f"   - Vollimport: {file}\n"
            instructions += f"   - DocType in ERPNext: {doctype}\n"
            instructions += f"   - Import Type: Insert New Records\n\n"
    
    instructions += """
## TEST-VERFAHREN:
1. 🧪 **TEST-Import** (TEST_*.csv Dateien)
   - Import Type: "Insert New Records"
   - Mute Emails: ✅ (aktiviert)
   - Submit after Import: ❌ (deaktiviert)
   
2. 🔍 **Validierung**
   - Prüfe ob Datensätze korrekt angelegt wurden
   - Prüfe Feldmappings
   - Teste Beziehungen zwischen Dokumenten
   
3. 🗑️ **Aufräumen**
   - TEST-Datensätze wieder löschen
   
4. ✅ **Vollimport**
   - Bei erfolgreichem Test: Vollständigen Import durchführen

## FEHLERBEHANDLUNG:
- Bei Mapping-Fehlern: Template-Download aus ERPNext verwenden
- Bei Validierungsfehlern: Feldwerte in CSV anpassen
- Bei Performance-Problemen: Größere Dateien in kleinere Chunks aufteilen

## BACKUP:
⚠️ **WICHTIG**: Vor Vollimport immer ERPNext-Backup erstellen!
"""
    
    return instructions

def main():
    """Vollständige Test-Pipeline"""
    print("🧪 ERPNext Import Test-Pipeline")
    print("=" * 60)
    
    # 1. Alle funktionsfähigen JSON-Dateien konvertieren
    working_files = ['artikel_chunk1.json']  # Erweitern sobald andere Dateien repariert sind
    csv_files = []
    
    for json_file in working_files:
        json_path = os.path.join('export', json_file)
        if os.path.exists(json_path):
            csv_file = convert_json_to_csv(json_path)
            if csv_file:
                csv_files.append(csv_file)
                validate_csv_export(csv_file)
                
                # Test-Sample erstellen
                create_test_sample(csv_file)
    
    # 2. Import-Anweisungen generieren
    if csv_files:
        instructions = generate_import_instructions(csv_files)
        
        with open('IMPORT_ANLEITUNG.md', 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"\n📖 Import-Anleitung erstellt: IMPORT_ANLEITUNG.md")
        print(f"📁 CSV-Dateien im Verzeichnis: ./csv_export/")
        
        print(f"\n🎯 NÄCHSTER SCHRITT:")
        print(f"   1. Lade die TEST_*.csv Dateien in ERPNext Data Import Tool")
        print(f"   2. Führe Test-Import durch (5 Datensätze)")
        print(f"   3. Bei Erfolg → Vollimport")
        
        return True
    else:
        print("❌ Keine CSV-Dateien erstellt")
        return False

if __name__ == "__main__":
    main()