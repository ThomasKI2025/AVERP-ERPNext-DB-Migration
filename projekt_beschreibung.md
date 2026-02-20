# Projekt-Spezifikation: Datenmigration AvERP zu ERPNext

## 1. Projekt-Kontext
* **Quell-System:** AvERP (Firebird SQL Datenbank, On-Premise)
* **Ziel-System:** ERPNext (MariaDB, Frappe Framework)
* **Zielsetzung:** Vollständige Migration (Stammdaten, Bewegungsdaten, Historie, Anhänge).
* **Strategie:** Zweistufiger Prozess (Offline-Export beim Kunden -> Lokale Transformation -> Import via API/Data-Import).

## 2. Technische Anforderungen (Exporter)
* **Sprache:** Python 3.x
* **Datenbank-Treiber:** `fdb` für Firebird-Anbindung.
* **Datenverarbeitung:** `pandas` zur Strukturierung der Daten.
* **Ausgabeformat:** JSON (bevorzugt wegen Verschachtelung) oder CSV.
* **Lauffähigkeit:** Muss On-Premise ohne Internetverbindung lauffähig sein (Portable Python Umgebung).

## 3. Datenbank-Struktur (Mapping-Fokus)
Folgende Kernbereiche müssen über SQL-Queries aus der `AVERP.FDB` extrahiert werden:

### A. Partner & Kontakte
- **Tabellen:** `BKUNDE` (Kunden), `BLIEFER` (Lieferanten), `BADR` (Adressen), `BKP` (Ansprechpartner).
- **Logik:** Adressen müssen über die `BADR_ID` mit Kunden/Lieferanten verknüpft werden.

### B. Materialwirtschaft (Items)
- **Tabellen:** `BSA` (Stamm), `BSAGR` (Warengruppen), `BSAUOM` (Einheiten), `BARTPR` (Preise).
- **Logik:** ERPNext benötigt zwingend eine `UOM` (Einheit) pro Artikel.

### C. Historie & Transaktionen (Deep Dive)
- **Verkauf:** `BAUF` / `BAUFP` (Aufträge/Positionen) & `BRECH` / `BRECHP` (Rechnungen/Positionen).
- **Einkauf:** `BBEST` / `BBESTP` (Bestellungen) & `BRLS` / `BRLSP` (Eingangsrechnungen).
- **Finanzen:** `BBS` / `BBSP` (Buchungssätze für Eröffnungsbilanz).

## 4. Anweisungen für Copilot (Prompting-Guideline)
Generiere ein modulares Python-Skript, das folgende Features enthält:
1.  **Config-Modul:** Trennung von DB-Credentials (DSN, User, PW) und Programmlogik.
2.  **Abfrage-Manager:** Ein Dictionary, das SQL-Queries speichert, um sie nacheinander abzuarbeiten.
3.  **Error-Handling:** Logging von fehlgeschlagenen Queries (z.B. bei fehlenden Tabellenrechten).
4.  **Daten-Sanitierung:** Konvertierung von Firebird-spezifischen Datentypen (z.B. Decimals, Blobs) in JSON-kompatible Formate.
5.  **Chunking:** Bei großen Tabellen (z.B. Lagerhistorie) soll der Export in Teil-Dateien erfolgen, um den Arbeitsspeicher zu schonen.

## 5. Bekannte AvERP Besonderheiten
- Zeichensatz ist oft `ISO8859_1` oder `UTF8`.
- Primärschlüssel in AvERP sind meist Generatoren/IDs, diese müssen als Referenz für das Mapping in ERPNext erhalten bleiben (`old_parent_id`).