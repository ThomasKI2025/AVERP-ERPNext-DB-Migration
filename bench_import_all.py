#!/usr/bin/env python3
# bench_import_all.py
# Erstellt Import-Skripte für bench console (umgeht API-Probleme)

import json
import os

def create_import_script(data_type, json_file, output_script):
    """Erstellt ein Import-Skript für bench console"""
    
    # Lade Daten
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Erstelle Skript basierend auf Datentyp
    if data_type == 'kunden':
        script = create_customer_script(data)
    elif data_type == 'werke':
        script = create_warehouse_script(data)
    elif data_type == 'banken':
        script = create_bank_script(data)
    elif data_type == 'eingangsrechnungen':
        script = create_purchase_invoice_script(data)
    else:
        print(f"⚠️  Kein Mapping für {data_type}")
        return False
    
    # Speichere Skript
    with open(output_script, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"✅ Skript erstellt: {output_script}")
    return True

def create_customer_script(data):
    """Erstellt Customer Import-Skript"""
    return f"""
import frappe
import json

print("Starte Kunden-Import...")
print(f"Datensätze: {len(data)}")

success = 0
errors = 0
skipped = 0

customers = {json.dumps(data, ensure_ascii=False, indent=2)}

for i, averp_kunde in enumerate(customers, 1):
    try:
        customer_name = str(averp_kunde.get('MASKENKEY', f'CUST_{{averp_kunde["ID"]}}'))
        
        if frappe.db.exists('Customer', customer_name):
            skipped += 1
            if i % 5 == 0:
                print(f"  [{{i}}/{len(data)}] ✅ {{success}} | ⏭️  {{skipped}} | ❌ {{errors}}")
            continue
        
        customer = frappe.get_doc({{
            'doctype': 'Customer',
            'customer_name': customer_name,
            'customer_type': 'Company',
            'customer_group': 'Alle Kundengruppen',
            'territory': 'Alle Gebiete'
        }})
        
        customer.insert(ignore_permissions=True)
        frappe.db.commit()
        success += 1
        
        if i % 5 == 0:
            print(f"  [{{i}}/{len(data)}] ✅ {{success}} | ⏭️  {{skipped}} | ❌ {{errors}}")
            
    except Exception as e:
        errors += 1
        print(f"  [{{i}}] ❌ {{customer_name}}: {{str(e)[:100]}}")
        frappe.db.rollback()

print()
print("=" * 60)
print(f"📊 Kunden-Import abgeschlossen!")
print(f"   ✅ Erfolgreich: {{success}}")
print(f"   ⏭️  Übersprungen: {{skipped}}")
print(f"   ❌ Fehler: {{errors}}")
print("=" * 60)
"""

def create_warehouse_script(data):
    """Erstellt Warehouse Import-Skript"""
    return f"""
import frappe
import json

print("Starte Werke/Warehouse-Import...")
print(f"Datensätze: {len(data)}")

success = 0
errors = 0
skipped = 0

werke = {json.dumps(data, ensure_ascii=False, indent=2)}

for i, averp_werk in enumerate(werke, 1):
    try:
        # Verwende MASKENKEY, WERKST oder WERKSTOFF als Name
        warehouse_name = (averp_werk.get('MASKENKEY') or 
                         averp_werk.get('WERKST') or 
                         averp_werk.get('WERKSTOFF') or 
                         f'WERK_{{averp_werk["ID"]}}')
        warehouse_name = str(warehouse_name).strip()
        
        if not warehouse_name or warehouse_name == 'None':
            warehouse_name = f'WERK_{{averp_werk["ID"]}}'
        
        if frappe.db.exists('Warehouse', warehouse_name):
            skipped += 1
            if i % 100 == 0:
                print(f"  [{{i}}/{len(data)}] ✅ {{success}} | ⏭️  {{skipped}} | ❌ {{errors}}")
            continue
        
        warehouse = frappe.get_doc({{
            'doctype': 'Warehouse',
            'warehouse_name': warehouse_name,
            'is_group': 0,
            'company': 'Your Company'
        }})
        
        warehouse.insert(ignore_permissions=True)
        frappe.db.commit()
        success += 1
        
        if i % 100 == 0:
            print(f"  [{{i}}/{len(data)}] ✅ {{success}} | ⏭️  {{skipped}} | ❌ {{errors}}")
            
    except Exception as e:
        errors += 1
        if errors <= 10:
            print(f"  [{{i}}] ❌ {{warehouse_name}}: {{str(e)[:100]}}")
        frappe.db.rollback()

print()
print("=" * 60)
print(f"📊 Warehouse-Import abgeschlossen!")
print(f"   ✅ Erfolgreich: {{success}}")
print(f"   ⏭️  Übersprungen: {{skipped}}")
print(f"   ❌ Fehler: {{errors}}")
print("=" * 60)
"""

def create_bank_script(data):
    """Erstellt Bank Import-Skript"""
    return f"""
import frappe
import json

print("Starte Banken-Import...")
print(f"Datensätze: {len(data)}")

success = 0
errors = 0
skipped = 0

banken = {json.dumps(data, ensure_ascii=False, indent=2)}

for i, averp_bank in enumerate(banken, 1):
    try:
        bank_name = str(averp_bank.get('BANKNAME', f'BANK_{{averp_bank["ID"]}}'))
        
        if frappe.db.exists('Bank', bank_name):
            skipped += 1
            if i % 100 == 0:
                print(f"  [{{i}}/{len(data)}] ✅ {{success}} | ⏭️  {{skipped}} | ❌ {{errors}}")
            continue
        
        bank = frappe.get_doc({{
            'doctype': 'Bank',
            'bank_name': bank_name
        }})
        
        # Optional: SWIFT Code
        if averp_bank.get('SWIFT'):
            bank.swift_number = averp_bank['SWIFT']
        
        bank.insert(ignore_permissions=True)
        frappe.db.commit()
        success += 1
        
        if i % 100 == 0:
            print(f"  [{{i}}/{len(data)}] ✅ {{success}} | ⏭️  {{skipped}} | ❌ {{errors}}")
            
    except Exception as e:
        errors += 1
        if errors <= 10:
            print(f"  [{{i}}] ❌ {{bank_name}}: {{str(e)[:100]}}")
        frappe.db.rollback()

print()
print("=" * 60)
print(f"📊 Bank-Import abgeschlossen!")
print(f"   ✅ Erfolgreich: {{success}}")
print(f"   ⏭️  Übersprungen: {{skipped}}")
print(f"   ❌ Fehler: {{errors}}")
print("=" * 60)
"""

def create_purchase_invoice_script(data):
    """Erstellt Purchase Invoice Import-Skript"""
    return f"""
import frappe
import json
from datetime import datetime

print("Starte Eingangsrechnungen-Import...")
print(f"Datensätze: {len(data)}")

success = 0
errors = 0
skipped = 0

rechnungen = {json.dumps(data, ensure_ascii=False, indent=2)}

for i, averp_rechnung in enumerate(rechnungen, 1):
    try:
        invoice_name = str(averp_rechnung.get('MASKENKEY', f'PINV_{{averp_rechnung["ID"]}}'))
        
        if frappe.db.exists('Purchase Invoice', invoice_name):
            skipped += 1
            continue
        
        # Erstelle Invoice
        invoice = frappe.get_doc({{
            'doctype': 'Purchase Invoice',
            'naming_series': 'PINV-',
            'supplier': 'Default Supplier',  # Muss angepasst werden
            'company': 'Your Company',
            'currency': 'EUR'
        }})
        
        # Datum
        if averp_rechnung.get('LIEFDATUM'):
            try:
                invoice.posting_date = datetime.strptime(
                    averp_rechnung['LIEFDATUM'], '%Y-%m-%d'
                ).date()
            except:
                pass
        
        invoice.insert(ignore_permissions=True)
        frappe.db.commit()
        success += 1
        print(f"  [{{i}}] ✅ {{invoice_name}}")
            
    except Exception as e:
        errors += 1
        print(f"  [{{i}}] ❌ {{invoice_name}}: {{str(e)[:100]}}")
        frappe.db.rollback()

print()
print("=" * 60)
print(f"📊 Purchase Invoice-Import abgeschlossen!")
print(f"   ✅ Erfolgreich: {{success}}")
print(f"   ⏭️  Übersprungen: {{skipped}}")
print(f"   ❌ Fehler: {{errors}}")
print("=" * 60)
"""

def main():
    print("="*60)
    print("🚀 Bench Console Import-Skripte Generator")
    print("="*60)
    print()
    
    export_path = './export'
    tmp_path = '/tmp'
    
    # Erstelle Import-Skripte
    scripts = [
        ('kunden', 'kunden_chunk1.json', 'import_customers.py'),
        ('werke', 'werke_chunk1.json', 'import_warehouses.py'),
        ('banken', 'banken_chunk1.json', 'import_banks.py'),
    ]
    
    created = []
    for data_type, json_file, script_name in scripts:
        json_path = os.path.join(export_path, json_file)
        script_path = os.path.join(tmp_path, script_name)
        
        if not os.path.exists(json_path):
            print(f"⏭️  {data_type}: JSON-Datei nicht gefunden")
            continue
        
        if create_import_script(data_type, json_path, script_path):
            created.append((data_type, script_name))
    
    print()
    print("="*60)
    print("✅ Import-Skripte erstellt!")
    print("="*60)
    print()
    print("Ausführen in bench console:")
    print()
    print("   sudo su - erpnext-user")
    print("   cd ~/frappe-bench")
    print("   bench console")
    print()
    print("Dann im Console:")
    for data_type, script_name in created:
        print(f"   exec(open('/tmp/{script_name}').read())  # {data_type}")
    print()

if __name__ == "__main__":
    main()
