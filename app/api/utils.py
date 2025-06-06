import re
from datetime import datetime
from typing import Tuple

def extract_week_and_year_from_filename(filename: str) -> Tuple[int, int]:
    """
    Extrahiert Woche und Jahr aus dem Dateinamen.
    Erwartetes Format im Dateinamen: 'KW12', 'Week12', 'kw12' oder 'week12'
    """
    week_match = re.search(r'(KW|Week)(\d{1,2})', filename, re.IGNORECASE)
    year_match = re.search(r'(\d{4})', filename)

    if not week_match:
        raise ValueError("KW konnte nicht aus dem Dateinamen extrahiert werden.")

    week = int(week_match.group(2))

    if year_match:
        year = int(year_match.group(1))
    else:
        year = datetime.utcnow().year  # Fallback aktuelles Jahr

    return week, year
