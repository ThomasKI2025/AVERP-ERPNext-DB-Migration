#!/bin/bash
# run_all_imports.sh
# Führt alle Imports nacheinander in bench console aus

echo "=================================="
echo "🚀 AVERP → ERPNext Vollständiger Import"
echo "=================================="
echo ""

cd /home/ubuntu/AVERP-to-ERPNext-Data-Migration

# Erstelle temporäres Python-Skript für bench
cat > /tmp/run_all_imports.py << 'EOF'
import frappe
import json
import sys

def import_customers():
    print("\n" + "="*60)
    print("📦 1/3: KUNDEN IMPORT")
    print("="*60)
    exec(open('/tmp/import_customers.py').read())

def import_warehouses():
    print("\n" + "="*60)
    print("📦 2/3: WERKE/WAREHOUSE IMPORT")
    print("="*60)
    exec(open('/tmp/import_warehouses.py').read())

def import_banks():
    print("\n" + "="*60)
    print("📦 3/3: BANKEN IMPORT")
    print("="*60)
    exec(open('/tmp/import_banks.py').read())

print("\n🚀 Starte vollständigen AVERP-Import...")
print("Datensätze: 15 Kunden + 4.343 Werke + 6.473 Banken (Rest)")
print()

try:
    import_customers()
    import_warehouses()
    import_banks()
    
    print("\n" + "="*60)
    print("✅ KOMPLETTER IMPORT ABGESCHLOSSEN!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
EOF

echo "Führe Import aus..."
echo ""

sudo -u erpnext-user /home/erpnext-user/frappe-bench/env/bin/python -c "
import sys
sys.path.insert(0, '/home/erpnext-user/frappe-bench/apps/frappe')
sys.path.insert(0, '/home/erpnext-user/frappe-bench/apps/erpnext')

import os
os.chdir('/home/erpnext-user/frappe-bench/sites')

import frappe
frappe.init(site='mysite.localhost')
frappe.connect()

exec(open('/tmp/run_all_imports.py').read())

frappe.destroy()
"

echo ""
echo "=================================="
echo "✅ Import-Prozess abgeschlossen!"
echo "=================================="
