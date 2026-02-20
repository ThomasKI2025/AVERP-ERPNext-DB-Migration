# utils.py
# Hilfsfunktionen für AvERP Exporter

import decimal
import datetime
import logging
import json

def setup_logger(logfile='exporter.log'):
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    return logging.getLogger()

def sanitize_value(val):
    if isinstance(val, decimal.Decimal):
        return float(val)
    if isinstance(val, (datetime.date, datetime.datetime, datetime.time)):
        return val.isoformat()
    if isinstance(val, bytes):
        try:
            return val.decode('utf-8')
        except Exception:
            return val.hex()
    return val

def sanitize_row(row):
    return {k: sanitize_value(v) for k, v in row.items()}

