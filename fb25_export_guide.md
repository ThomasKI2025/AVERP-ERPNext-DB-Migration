# fb25_export_guide.md
# Anleitung zum Export der AvERP-Daten

## Problem
Die lokalen Firebird-Dateien wurden mit Version 2.5 erstellt, aber das System hat Version 3.0 installiert.

## Lösungsvorschläge:

### Option 1: Export auf dem ursprünglichen System
Führe das Export-Skript direkt auf dem System aus, wo AvERP läuft (mit Firebird 2.5).

### Option 2: Firebird 2.5 Installation
1. Lade Firebird 2.5 für Linux herunter
2. Installiere es parallel zur Version 3.0
3. Verwende die 2.5 Client-Bibliotheken

### Option 3: SQL-Dumps erstellen
Auf dem AvERP-System mit Firebird 2.5:
```bash
isql-fb -u SYSDBA -p masterkey Produktiv.FDB -o dump_kunden.sql -q "SELECT * FROM BKUNDE;"
isql-fb -u SYSDBA -p masterkey Produktiv.FDB -o dump_artikel.sql -q "SELECT * FROM BSA;"
# Weitere Tabellen...
```

### Option 4: CSV-Export über AvERP
Falls AvERP eine Export-Funktion hat, nutze diese um CSV-Dateien zu erstellen.

## Nächste Schritte
1. Prüfe welche Option am praktikabelsten ist
2. Führe den Export entsprechend durch
3. Verwende dann das vorbereitete Import-Skript für ERPNext