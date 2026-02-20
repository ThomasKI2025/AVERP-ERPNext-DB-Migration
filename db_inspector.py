# db_inspector.py
# Hilfsskript zur Analyse der Datenbankstruktur

import os
import subprocess
from config import DB_CONFIG

def analyze_db_file():
    """Analysiert die Firebird-Datenbankdatei"""
    db_path = DB_CONFIG['dsn']
    
    print(f"Analysiere: {db_path}")
    
    # Dateigröße prüfen
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / (1024*1024)  # MB
        print(f"Dateigröße: {size:.2f} MB")
    else:
        print("Datei nicht gefunden!")
        return
    
    # Versuche verschiedene Firebird-Tools
    tools_to_try = ['isql-fb', 'isql', 'fbsql']
    
    for tool in tools_to_try:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Gefunden: {tool} -> {result.stdout.strip()}")
                
                # Versuche eine einfache Verbindung
                cmd = [tool, '-u', DB_CONFIG['user'], '-p', DB_CONFIG['password'], db_path]
                print(f"Versuche Verbindung mit: {' '.join(cmd[:3])} [password] {db_path}")
                
        except Exception as e:
            print(f"Fehler bei {tool}: {e}")

def check_firebird_version():
    """Prüft installierte Firebird-Version"""
    try:
        result = subprocess.run(['firebird', '--version'], capture_output=True, text=True)
        print(f"Firebird Version: {result.stdout}")
    except:
        print("Firebird Kommandozeile nicht verfügbar")

if __name__ == "__main__":
    analyze_db_file()
    check_firebird_version()