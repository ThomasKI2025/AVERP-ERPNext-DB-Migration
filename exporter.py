# exporter.py
# Hauptmodul für AvERP Datenexport

import pandas as pd
import os
import json
from config import DB_CONFIG, EXPORT_PATH, CHUNK_SIZE
from queries import QUERIES
from utils import setup_logger, sanitize_row

logger = setup_logger()

def get_connection():
    """Versucht verschiedene Firebird-Treiber für die Verbindung"""
    try:
        import fdb
        return fdb.connect(**DB_CONFIG)
    except Exception as e:
        logger.info(f"fdb Treiber fehlgeschlagen: {e}")
        try:
            import firebirdsql
            config = DB_CONFIG.copy()
            config['database'] = config.pop('dsn')
            return firebirdsql.connect(**config)
        except Exception as e2:
            logger.error(f"Beide Treiber fehlgeschlagen - fdb: {e}, firebirdsql: {e2}")
            raise e2

def export_table(conn, name, query):
    logger.info(f"Starte Export: {name}")
    try:
        df_iter = pd.read_sql(query, conn, chunksize=CHUNK_SIZE)
        chunk_count = 0
        for i, chunk in enumerate(df_iter):
            # Sanitize data for JSON compatibility
            sanitized_data = []
            for _, row in chunk.iterrows():
                sanitized_data.append(sanitize_row(row.to_dict()))
            
            out_file = os.path.join(EXPORT_PATH, f"{name}_chunk{i+1}.json")
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(sanitized_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exportiert: {out_file} ({len(sanitized_data)} Datensätze)")
            chunk_count += 1
        
        if chunk_count == 0:
            logger.warning(f"Keine Daten gefunden für: {name}")
    except Exception as e:
        logger.error(f"Fehler beim Export von {name}: {e}")

def main():
    if not os.path.exists(EXPORT_PATH):
        os.makedirs(EXPORT_PATH)
    try:
        conn = get_connection()
        logger.info("Datenbankverbindung erfolgreich hergestellt")
        
        for name, query in QUERIES.items():
            export_table(conn, name, query)
        conn.close()
        logger.info("Export abgeschlossen")
    except Exception as e:
        logger.error(f"DB-Verbindungsfehler: {e}")

if __name__ == "__main__":
    main()
