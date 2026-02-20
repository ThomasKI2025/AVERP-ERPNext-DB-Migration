# queries.py
# SQL-Query-Manager für AvERP Exporter

# queries.py
# SQL-Query-Manager für AvERP Exporter - Echte Tabellen aus der Datenbank

QUERIES = {
    # Stammdaten
    'kunden': "SELECT * FROM BKUNDE",
    'adressen': "SELECT * FROM BADR", 
    'artikel': "SELECT * FROM BSA",
    'postleitzahlen': "SELECT * FROM BPLZ",
    'banken': "SELECT * FROM BSBANK",
    'werke': "SELECT * FROM BWERK",
    
    # Bewegungsdaten  
    'eingangsrechnungen': "SELECT * FROM BRLS",
    'eingangsrechnungspositionen': "SELECT * FROM BRLSP",
    
    # System/Meta-Daten
    'felder': "SELECT * FROM A_FELDER",
    'tabellen': "SELECT * FROM A_TABELLEN",
    'masken': "SELECT * FROM A_MASKEN",
    
    # Große Datenmengen (falls relevant)
    'transport_daten': "SELECT * FROM A_TRANSP LIMIT 1000",  # Begrenzt wegen Größe
    'transaktionen': "SELECT * FROM A_TRANS LIMIT 1000",
}
