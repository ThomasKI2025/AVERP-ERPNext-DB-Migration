# erpnext_config.py
# Konfiguration für ERPNext Import

# ERPNext Server Einstellungen
ERPNEXT_CONFIG = {
    'url': 'http://localhost:8000',
    'api_key': 'your_api_key_here',
    'api_secret': 'your_api_secret_here'
}

# Erweiterte Feld-Mappings für alle Datentypen
DOCTYPE_MAPPINGS = {
    'kunden': {
        'erpnext_doctype': 'Customer',
        'required_fields': ['customer_name'],
        'field_mapping': {
            'ID': 'customer_name',
            'MASKENKEY': 'customer_code',
            'EIG_LIEFNR': 'customer_primary_contact',
            'ERFDATUM': 'creation',
            'AKTIV_JN': 'disabled',
            'KRELIMIT': 'credit_limit',
            'BADR_ID_ADRNR': 'customer_primary_address'
        }
    },
    'artikel': {
        'erpnext_doctype': 'Item',
        'required_fields': ['item_code', 'item_name'],
        'field_mapping': {
            'ID': 'item_code',
            'BEZEICH': 'item_name',
            'EKNETTO': 'standard_rate',
            'AKTIV_JN': 'disabled',
            'ARTGR': 'item_group'
        }
    },
    'adressen': {
        'erpnext_doctype': 'Address',
        'required_fields': ['address_title'],
        'field_mapping': {
            'ID': 'address_title',
            'STRASSE': 'address_line1',
            'PLZ': 'pincode',
            'ORT': 'city'
        }
    }
}

# Import-Reihenfolge (wichtig für Referenzen)
IMPORT_ORDER = [
    'adressen',     # Zuerst Adressen
    'kunden',       # Dann Kunden (referenzieren Adressen)  
    'artikel',      # Artikel
    'eingangsrechnungen',
    'eingangsrechnungspositionen'
]