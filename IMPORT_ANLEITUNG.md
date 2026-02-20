
# 🚀 ERPNext Import-Anleitung

## VORBEREITUNG:
1. ERPNext öffnen → Setup → Data Import and Settings → Data Import
2. Zuerst mit TEST-Dateien (5 Datensätze) beginnen!

## IMPORT-REIHENFOLGE (WICHTIG!):

2. **Item**
   - Test: ./csv_export/Item_artikel_chunk1_TEST.csv
   - Vollimport: ./csv_export/Item_artikel_chunk1.csv
   - DocType in ERPNext: Item
   - Import Type: Insert New Records


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
