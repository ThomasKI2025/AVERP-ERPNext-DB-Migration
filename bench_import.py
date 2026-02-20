#!/usr/bin/env python3
"""
Direkter ERPNext Import über bench console (kein API)
Dieser Ansatz umgeht die API-Probleme
"""

import json
import os

def create_import_script():
    """Erstellt ein Python-Skript für bench console"""
    
    script = """
import frappe
import json

# Lade Artikel-Daten
with open('/tmp/artikel_chunk1.json', 'r') as f:
    artikel_data = json.load(f)

print(f"Gefunden: {len(artikel_data)} Artikel")
print("Starte vollständigen Import...")
print()

success = 0
errors = 0
skipped = 0

for i, averp_artikel in enumerate(artikel_data, 1):
    try:
        item_code = str(averp_artikel.get('MASKENKEY', f'ITEM_{averp_artikel["ID"]}'))
        
        # Prüfe ob bereits existiert
        if frappe.db.exists('Item', item_code):
            skipped += 1
            if i % 100 == 0:
                print(f"  [{i}/{len(artikel_data)}] ✅ {success} | ⏭️  {skipped} | ❌ {errors}")
            continue
        
        # Erstelle Item
        item = frappe.get_doc({
            'doctype': 'Item',
            'item_code': item_code,
            'item_name': averp_artikel.get('ARTBEZ', 'Unbekannt'),
            'item_group': 'Produkte',
            'stock_uom': 'Stk',
            'is_stock_item': 1,
            'disabled': 0 if averp_artikel.get('AKTIV_JN') == 'J' else 1
        })
        
        # Optional: Beschreibung
        if averp_artikel.get('ARTBEZ2'):
            item.description = averp_artikel['ARTBEZ2']
        
        item.insert(ignore_permissions=True)
        frappe.db.commit()
        success += 1
        
        # Fortschritt alle 100 Einträge
        if i % 100 == 0:
            print(f"  [{i}/{len(artikel_data)}] ✅ {success} | ⏭️  {skipped} | ❌ {errors}")
            
    except Exception as e:
        errors += 1
        if errors <= 10:  # Zeige nur erste 10 Fehler
            print(f"  [{i}] ❌ {item_code}: {str(e)[:100]}")
        frappe.db.rollback()

print()
print("=" * 60)
print(f"📊 Import abgeschlossen!")
print(f"   ✅ Erfolgreich: {success}")
print(f"   ⏭️  Übersprungen: {skipped}")
print(f"   ❌ Fehler: {errors}")
print("=" * 60)
"""
    
    with open('/tmp/import_items.py', 'w') as f:
        f.write(script)
    
    print("✅ Import-Skript erstellt: /tmp/import_items.py")
    print()
    print("🚀 Führen Sie aus:")
    print()
    print("   sudo su - erpnext-user")
    print("   cd ~/frappe-bench")
    print("   bench console")
    print()
    print("Dann im Console:")
    print()
    print("   exec(open('/tmp/import_items.py').read())")
    print()

if __name__ == '__main__':
    create_import_script()
