from pdfplumber import open as open_pdf
import re
from pathlib import Path


def extract_kw_from_filename(filename: str) -> str:
    match = re.search(r"(KW|Week)[-_]?\d{1,2}", filename, re.IGNORECASE)
    return match.group(0).replace("_", "-").upper() if match else "KW?"


def extract_scorecard_data(pdf_path: Path) -> dict:
    import re
    from pdfplumber import open as open_pdf

    with open_pdf(str(pdf_path)) as pdf:
        text = pdf.pages[1].extract_text()  # Seite 2

    # Text glätten
    flat_text = text.replace("\n", " ")

    overall_score = None
    rank = None
    focus_areas = []

    # 1. Overall Score (Beispiel: 75.22 | Great)
    score_match = re.search(r"Overall Score:\s*([0-9]{2,3}\.[0-9]{1,2})\s*\|", flat_text, re.IGNORECASE)
    if score_match:
        overall_score = float(score_match.group(1))

    # 2. Rank (Beispiel: Rank at DSU1: 6)
    rank_match = re.search(r"Rank at DSU1[:\s]*([0-9]+)", flat_text, re.IGNORECASE)
    if rank_match:
        rank = int(rank_match.group(1))

    # 3. Focus Areas (ab "Recommended Focus Areas")
    if "Recommended Focus Areas" in text:
        focus_block = text.split("Recommended Focus Areas")[-1]
        focus_areas = re.findall(r"\d+\.\s+(.*?)\n", focus_block)

    return {
        "overall_score": overall_score,
        "rank": rank,
        "focus_areas": focus_areas
    }


def extract_firm_kpis_from_pdf(pdf_path: Path) -> dict:
    import re
    from pdfplumber import open as open_pdf

    with open_pdf(str(pdf_path)) as pdf:
        text = pdf.pages[1].extract_text()

    firm_kpis = []

    # Wir splitten den Text in Zeilen
    lines = text.split("\n")

    pattern = re.compile(r"([0-9]+(?:\.[0-9]+)?%?)\s*\|\s*(Fantastic|Great|Fair|Poor|In Compliance|None|Not in Compliance)", re.IGNORECASE)

    for line in lines:
        match = pattern.search(line)
        if match:
            value = match.group(1)
            status = match.group(2).strip().capitalize()

            # Der KPI-Name steht links vom Wert
            name = line[:match.start()].strip()
            name = re.sub(r"\s+", " ", name)  # doppelte Leerzeichen entfernen

            firm_kpis.append({
                "name": name,
                "value": value,
                "status": status
            })

    # Sonderfall: Breach of Contract (BOC)
    boc_match = re.search(r"Breach of Contract \(BOC\)\s+(None|Not in Compliance)", text, re.IGNORECASE)
    if boc_match:
        firm_kpis.append({
            "name": "Breach of Contract (BOC)",
            "value": boc_match.group(1),
            "status": boc_match.group(1).capitalize()
        })

    return {
        "metrics": firm_kpis
    }
