from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import pdfplumber
import re
import io

from app.database import get_db
from app.models.scorecard_driver import ScorecardDriver
from app.models.employee import Employee
from app.models.firm_scorecard import FirmScorecard

router = APIRouter()

# --- Parser Hilfsfunktionen ---
def parse_int(value: str):
    value = value.strip()
    if value == "-" or value == "":
        return None
    return int(value)

def parse_float(value: str):
    value = value.strip().replace("%", "").replace(",", ".")
    if value == "-" or value == "":
        return None
    return float(value)

def normalize_transporter_id(tid: str) -> str:
    if not tid.startswith("A") and len(tid) == 13:
        return "A" + tid
    return tid

def extract_week_from_filename(filename: str) -> int:
    match = re.search(r"Week(\d{1,2})", filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    raise ValueError("Keine gültige KW im Dateinamen gefunden.")

# --- POST: Upload und Verarbeitung ---
@router.post("/scorecard/upload_combined_scorecard/")
async def upload_combined_scorecard(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        pdf = pdfplumber.open(io.BytesIO(contents))

        week = extract_week_from_filename(file.filename)
        year = 2025

        employees = db.query(Employee).all()
        transporter_id_map = {emp.transporter_id: emp.name for emp in employees if emp.transporter_id}

        # --- Seite 3+4: Fahrerdaten ---
        text = ""
        if len(pdf.pages) >= 3:
            text += pdf.pages[2].extract_text()
        if len(pdf.pages) >= 4:
            text += "\n" + pdf.pages[3].extract_text()

        pattern_driver = r'([A-Z0-9]{13,14})[\s\n]+(\d+)[\s\n]+([\d.,%-]+)[\s\n]+(\d+)[\s\n]+([\d.,%-]+)[\s\n]+([\d.,%-]+)[\s\n]+(\d+)[\s\n]+([\d.,%-]+)'
        matches = re.findall(pattern_driver, text)

        for match in matches:
            transporter_id, delivered, dcr, dnr_dpmo, pod, cc, ce, dex = match
            transporter_id = normalize_transporter_id(transporter_id)
            name = transporter_id_map.get(transporter_id, transporter_id)

            driver = ScorecardDriver(
                week=week,
                year=year,
                name=name,
                delivered=parse_int(delivered),
                dcr=parse_float(dcr),
                dnr_dpmo=parse_int(dnr_dpmo),
                pod=parse_float(pod),
                cc=parse_float(cc),
                ce=parse_int(ce),
                dex=parse_float(dex),
            )
            db.add(driver)

        # --- Seite 2: Firm KPIs ---
        firm_text = ""
        if len(pdf.pages) >= 2:
            firm_text = pdf.pages[1].extract_text()

        kpi_patterns = {
            "dcr": r"Delivery Completion Rate\(DCR\)[\s:]*([\d.,]+)%",
            "dnr_dpmo": r"Delivered Not Received\(DNR DPMO\)[\s:]*([\d.,]+)",
            "lor_dpmo": r"Lost on Road \(LoR\) DPMO[\s:]*([\d.,]+)",
        }

        firm_kpis = {
            key: parse_float(re.search(pat, firm_text).group(1))
            if re.search(pat, firm_text) else None
            for key, pat in kpi_patterns.items()
        }

        firm = FirmScorecard(
            week=week,
            year=year,
            dcr=firm_kpis["dcr"],
            dnr_dpmo=parse_int(str(firm_kpis["dnr_dpmo"]) if firm_kpis["dnr_dpmo"] is not None else ""),
            lor_dpmo=parse_int(str(firm_kpis["lor_dpmo"]) if firm_kpis["lor_dpmo"] is not None else ""),
        )
        db.add(firm)

        db.commit()
        return {"message": f"{len(matches)} Fahrer + Firmen-KPIs für KW {week} gespeichert."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
