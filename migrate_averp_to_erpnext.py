#!/usr/bin/env python3
# migrate_averp_to_erpnext.py
# Komplette Pipeline: AVERP FDB → JSON → ERPNext

import os
import sys
import json
import argparse
from datetime import datetime

class AVERPtoERPNextMigration:
    """Vollständige Migrationspipeline von AVERP zu ERPNext"""
    
    def __init__(self, fdb_path=None, skip_export=False):
        self.fdb_path = fdb_path
        self.skip_export = skip_export
        self.export_path = './export/'
        self.log_file = f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
    def log(self, message, level="INFO"):
        """Logging mit Zeitstempel"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        with open(self.log_file, 'a') as f:
            f.write(log_entry + '\n')
    
    def step1_check_fdb(self):
        """Schritt 1: Prüfe AVERP FDB-Datei"""
        self.log("=" * 60)
        self.log("SCHRITT 1: AVERP Datenbank-Prüfung")
        self.log("=" * 60)
        
        if self.skip_export:
            self.log("Export übersprungen (--skip-export)", "INFO")
            return True
            
        if not self.fdb_path:
            self.log("Keine FDB-Datei angegeben", "WARNING")
            self.log("Verwende vorhandene JSON-Dateien in export/", "INFO")
            return True
            
        if not os.path.exists(self.fdb_path):
            self.log(f"FDB-Datei nicht gefunden: {self.fdb_path}", "ERROR")
            return False
            
        self.log(f"FDB-Datei gefunden: {self.fdb_path}", "SUCCESS")
        return True
    
    def step2_export_averp(self):
        """Schritt 2: Exportiere Daten aus AVERP FDB"""
        self.log("\n" + "=" * 60)
        self.log("SCHRITT 2: AVERP Datenexport")
        self.log("=" * 60)
        
        if self.skip_export:
            self.log("Export übersprungen", "INFO")
            return True
            
        if not self.fdb_path:
            self.log("Überspringe Export - verwende vorhandene Dateien", "INFO")
            return True
        
        try:
            # Update config.py mit FDB-Pfad
            self.log(f"Aktualisiere config.py mit FDB-Pfad...", "INFO")
            with open('config.py', 'r') as f:
                config_content = f.read()
            
            # Ersetze FDB-Pfad
            import re
            new_config = re.sub(
                r"'dsn':\s*'[^']*'",
                f"'dsn': '{self.fdb_path}'",
                config_content
            )
            
            with open('config.py', 'w') as f:
                f.write(new_config)
            
            self.log("Starte exporter.py...", "INFO")
            import exporter
            exporter.main()
            
            self.log("Datenexport abgeschlossen", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Export fehlgeschlagen: {e}", "ERROR")
            return False
    
    def step3_validate_exports(self):
        """Schritt 3: Validiere exportierte JSON-Dateien"""
        self.log("\n" + "=" * 60)
        self.log("SCHRITT 3: JSON-Validierung")
        self.log("=" * 60)
        
        if not os.path.exists(self.export_path):
            self.log(f"Export-Verzeichnis nicht gefunden: {self.export_path}", "ERROR")
            return False
        
        json_files = [f for f in os.listdir(self.export_path) if f.endswith('.json')]
        
        if not json_files:
            self.log("Keine JSON-Dateien gefunden!", "ERROR")
            return False
        
        self.log(f"Gefunden: {len(json_files)} JSON-Dateien", "INFO")
        
        valid_count = 0
        error_count = 0
        
        for filename in sorted(json_files):
            filepath = os.path.join(self.export_path, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                self.log(f"  ✅ {filename:40s} - {len(data):6d} Datensätze", "INFO")
                valid_count += 1
            except Exception as e:
                self.log(f"  ❌ {filename:40s} - Fehler: {str(e)[:50]}", "ERROR")
                error_count += 1
        
        self.log(f"\nValidierung: {valid_count} OK, {error_count} Fehler", "INFO")
        return error_count == 0
    
    def step4_test_erpnext_connection(self):
        """Schritt 4: Teste ERPNext API-Verbindung"""
        self.log("\n" + "=" * 60)
        self.log("SCHRITT 4: ERPNext Verbindungstest")
        self.log("=" * 60)
        
        try:
            import requests
            
            # Lade Credentials
            if not os.path.exists('erpnext_credentials.json'):
                self.log("erpnext_credentials.json nicht gefunden!", "ERROR")
                self.log("Bitte ausführen: ./setup_credentials.sh", "INFO")
                return False
            
            with open('erpnext_credentials.json', 'r') as f:
                creds = json.load(f)
            
            url = creds.get('url', 'http://localhost:8000')
            api_key = creds['api_key']
            api_secret = creds['api_secret']
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'token {api_key}:{api_secret}'
            }
            
            response = requests.get(
                f"{url}/api/method/frappe.auth.get_logged_user",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json().get('message')
                self.log(f"✅ Verbunden als: {user}", "SUCCESS")
                self.log(f"   URL: {url}", "INFO")
                return True
            else:
                self.log(f"Verbindung fehlgeschlagen: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Verbindungsfehler: {e}", "ERROR")
            return False
    
    def step5_import_data(self, data_types=None):
        """Schritt 5: Importiere Daten nach ERPNext"""
        self.log("\n" + "=" * 60)
        self.log("SCHRITT 5: ERPNext Datenimport")
        self.log("=" * 60)
        
        if data_types is None:
            data_types = ['artikel', 'kunden']  # Standard-Import
        
        try:
            import erpnext_importer
            
            for data_type in data_types:
                file_path = os.path.join(self.export_path, f'{data_type}_chunk1.json')
                
                if not os.path.exists(file_path):
                    self.log(f"⏭️  {data_type}: Datei nicht gefunden", "WARNING")
                    continue
                
                self.log(f"\n📦 Importiere: {data_type}", "INFO")
                success, errors, skipped = erpnext_importer.import_json_to_erpnext(
                    data_type, file_path, skip_existing=True
                )
                
                self.log(f"   ✅ Erfolgreich: {success}", "SUCCESS")
                self.log(f"   ⏭️  Übersprungen: {skipped}", "INFO")
                self.log(f"   ❌ Fehler: {errors}", "ERROR" if errors > 0 else "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"Import fehlgeschlagen: {e}", "ERROR")
            return False
    
    def run(self, data_types=None):
        """Führe komplette Pipeline aus"""
        self.log("🚀 AVERP → ERPNext Migration Pipeline")
        self.log(f"Log-Datei: {self.log_file}")
        
        # Schritt 1: FDB-Prüfung
        if not self.step1_check_fdb():
            self.log("\n❌ Migration abgebrochen - FDB-Prüfung fehlgeschlagen", "ERROR")
            return False
        
        # Schritt 2: Export
        if not self.step2_export_averp():
            self.log("\n❌ Migration abgebrochen - Export fehlgeschlagen", "ERROR")
            return False
        
        # Schritt 3: Validierung
        if not self.step3_validate_exports():
            self.log("\n⚠️  Warnung: JSON-Validierung hat Fehler", "WARNING")
            response = input("Trotzdem fortfahren? (ja/nein): ")
            if response.lower() not in ['ja', 'j', 'yes', 'y']:
                self.log("Migration abgebrochen", "INFO")
                return False
        
        # Schritt 4: ERPNext Connection
        if not self.step4_test_erpnext_connection():
            self.log("\n❌ Migration abgebrochen - ERPNext Verbindung fehlgeschlagen", "ERROR")
            return False
        
        # Schritt 5: Import
        if not self.step5_import_data(data_types):
            self.log("\n❌ Migration mit Fehlern abgeschlossen", "ERROR")
            return False
        
        self.log("\n" + "=" * 60)
        self.log("✅ Migration erfolgreich abgeschlossen!")
        self.log("=" * 60)
        self.log(f"Log gespeichert: {self.log_file}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Komplette AVERP zu ERPNext Migrationspipeline'
    )
    parser.add_argument(
        '--fdb',
        help='Pfad zur AVERP FDB-Datei (optional, verwendet vorhandene JSONs wenn nicht angegeben)'
    )
    parser.add_argument(
        '--skip-export',
        action='store_true',
        help='Überspringe Export-Schritt, verwende vorhandene JSON-Dateien'
    )
    parser.add_argument(
        '--data-types',
        nargs='+',
        default=['artikel', 'kunden'],
        help='Datentypen zum Import (Standard: artikel kunden)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interaktiver Modus mit Benutzerabfragen'
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        print("="*60)
        print("🚀 AVERP → ERPNext Migration (Interaktiv)")
        print("="*60)
        print()
        
        # FDB-Pfad abfragen
        fdb_default = '/pfad/zur/averp.fdb'
        fdb_path = input(f"AVERP FDB-Pfad (Enter für vorhandene JSONs): ").strip()
        if not fdb_path:
            fdb_path = None
        
        # Datentypen auswählen
        print("\nVerfügbare Datentypen:")
        print("  1. artikel (Artikel/Items)")
        print("  2. kunden (Kunden/Customers)")
        print("  3. banken (Banken)")
        print("  4. werke (Werke/Warehouses)")
        print("  5. eingangsrechnungen (Lieferantenrechnungen)")
        print("  6. Alle wichtigen Datentypen")
        
        choice = input("\nAuswahl (z.B. 1,2 oder 6): ").strip()
        
        if choice == '6':
            data_types = ['artikel', 'kunden', 'werke', 'banken', 'eingangsrechnungen']
        else:
            type_map = {
                '1': 'artikel',
                '2': 'kunden', 
                '3': 'banken',
                '4': 'werke',
                '5': 'eingangsrechnungen'
            }
            data_types = [type_map[c.strip()] for c in choice.split(',') if c.strip() in type_map]
        
        migration = AVERPtoERPNextMigration(
            fdb_path=fdb_path,
            skip_export=(fdb_path is None)
        )
        migration.run(data_types=data_types)
        
    else:
        # Nicht-interaktiver Modus
        migration = AVERPtoERPNextMigration(
            fdb_path=args.fdb,
            skip_export=args.skip_export
        )
        migration.run(data_types=args.data_types)


if __name__ == "__main__":
    main()
