# ERPNext Import Analysis
# Basierend auf der Analyse des ERPNext Source Codes

## 🔍 GEFUNDENE IMPORT-METHODEN IN ERPNEXT:

### 1. **FRAPPE DATA IMPORT FRAMEWORK** ⭐⭐⭐
**Gefunden in:** `frappe.core.doctype.data_import`
- **Standard-Import-Mechanism** für alle DocTypes
- **Unterstützt:** CSV, XLSX, JSON
- **Features:** Bulk Import, Update/Insert Modi, Template-Generierung
- **UI:** Webbasierte Import-Oberfläche im ERPNext

### 2. **CHART OF ACCOUNTS IMPORTER** ⭐⭐
**Gefunden in:** `erpnext.accounts.doctype.chart_of_accounts_importer`
- **CSV/XLSX Import** für Kontenplan
- **Template-basiert** mit 8 Spalten
- **Validierung** von Datenstruktur

### 3. **BANK STATEMENT IMPORT** ⭐⭐
**Gefunden in:** `erpnext.accounts.doctype.bank_statement_import`
- **Erweitert** das Standard Data Import Framework
- **CSV/XLSX Support** mit benutzerdefinierten Trennzeichen
- **Background Jobs** für große Dateien

### 4. **PROGRAMMIERTER IMPORT** ⭐⭐⭐
**Standard Frappe-Pattern:**
```python
# Methode 1: Via Document API
doc = frappe.get_doc({"doctype": "Customer", "customer_name": "Test"})
doc.insert()

# Methode 2: Bulk Insert via SQL
frappe.db.bulk_insert(doctype, fields, values)
```

## 📋 EMPFOHLENE IMPORT-STRATEGIEN:

### **OPTION 1: CSV + DATA IMPORT TOOL** 🥇
**Pro:**
- ✅ Nutzt ERPNext Standard-Mechanismus
- ✅ Webbasierte UI verfügbar
- ✅ Automatische Validierung & Fehlerbehandlung
- ✅ Template-Download möglich
- ✅ Batch-Processing für große Dateien

**Contra:**
- ❌ Erfordert CSV-Konvertierung
- ❌ Feldmapping manuell über UI

**Umsetzung:**
1. JSON → CSV Konverter erstellen
2. ERPNext Data Import Tool verwenden

### **OPTION 2: DIREKTE SQL INSERTS** 🥈
**Pro:**
- ✅ Maximale Performance
- ✅ Direkte Datenbankanbindung
- ✅ Bulk Operations möglich

**Contra:**
- ❌ Umgeht ERPNext Validierungen
- ❌ Keine Workflow-Trigger
- ❌ Referenzen müssen manuell aufgelöst werden

### **OPTION 3: PYTHON API IMPORT** 🥉
**Pro:**
- ✅ Vollständige ERPNext Integration
- ✅ Automatische Validierung
- ✅ Workflow-Trigger funktionieren

**Contra:**
- ❌ Langsamer bei großen Datenmengen
- ❌ Erfordert ERPNext-Installation

## 🎯 MEINE EMPFEHLUNG:

**Kombinationsansatz:**
1. **CSV-Konverter** für Standard-DocTypes (Customer, Item, etc.)
2. **Python-Skript** mit Frappe API für komplexe Referenzen
3. **SQL-Inserts** für große Datenmengen ohne Logik

Soll ich einen detaillierten Plan für eine dieser Optionen erstellen?