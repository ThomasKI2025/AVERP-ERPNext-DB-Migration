# config.py
# Konfigurationsdatei für AvERP Exporter

DB_CONFIG = {
    'dsn': '/home/ubuntu/AVERP-to-ERPNext-Data-Migration/averp-database.fdb',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'WIN1252',  # Alternative Zeichensatz
}

EXPORT_PATH = './export/'
CHUNK_SIZE = 10000  # Anzahl Datensätze pro Export-Chunk
