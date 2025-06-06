from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import pdfplumber
import re
import io
from sqlalchemy import Column, Integer, Float

from app.database import get_db, Base
from app.models.scorecard_driver import ScorecardDriver
from app.models.employee import Employee
# from app.models.firm_scorecard import FirmScorecard, ScorecardFirm

router = APIRouter()

def extract_week_from_filename(filename: str) -> int:
    match = re.search(r'Week(\d{1,2})', filename)
    if match:
        return int(match.group(1))
    raise ValueError("Keine gültige KW im Dateinamen gefunden.")

def parse_int(value):
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if value == '-' or value == '':
            return None
        return int(float(value))
    return None

def parse_float(value):
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip().replace('%', '').replace(',', '.')
        if value == '-' or value == '':
            return None
        return float(value)
    return None

def normalize_transporter_id(tid: str) -> str:
    if not tid.startswith("A") and len(tid) == 13:
        return "A" + tid
    return tid

@router.post("/scorecard/upload_driver_scorecard/")
async def upload_driver_scorecard(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        pdf = pdfplumber.open(io.BytesIO(contents))

        week = extract_week_from_filename(file.filename)
        year = 2025

        employees = db.query(Employee).all()
        transporter_id_map = {emp.transporter_id: emp.name for emp in employees if emp.transporter_id}

        text = ""
        if len(pdf.pages) >= 3:
            text += pdf.pages[2].extract_text()
        if len(pdf.pages) >= 4:
            text += "\n" + pdf.pages[3].extract_text()

        pattern_with_lor = r'([A-Z0-9]{13,14})[\s\n]+(\d+)[\s\n]+([\d.,%-]+)[\s\n]+(\d+)[\s\n]+(\d+)[\s\n]+([\d.,%-]+)[\s\n]+([\d.,%-]+)[\s\n]+(\d+)[\s\n]+([\d.,%-]+)'
        pattern_without_lor = r'([A-Z0-9]{13,14})[\s\n]+(\d+)[\s\n]+([\d.,%-]+)[\s\n]+(\d+)[\s\n]+([\d.,%-]+)[\s\n]+([\d.,%-]+)[\s\n]+(\d+)[\s\n]+([\d.,%-]+)'

        matches = re.findall(pattern_with_lor, text)
        pattern_used = "with_lor"

        if not matches:
            matches = re.findall(pattern_without_lor, text)
            pattern_used = "without_lor"

        if not matches:
            raise HTTPException(status_code=400, detail="Keine Fahrer-Daten in der Scorecard gefunden.")

        for match in matches:
            if pattern_used == "with_lor":
                transporter_id, delivered, dcr, dnr_dpmo, lor_dpmo, pod, cc, ce, dex = match
            else:
                transporter_id, delivered, dcr, dnr_dpmo, pod, cc, ce, dex = match
                lor_dpmo = None

            transporter_id = normalize_transporter_id(transporter_id)
            name = transporter_id_map.get(transporter_id, transporter_id)

            driver = ScorecardDriver(
                week=week,
                year=year,
                name=name,
                delivered=parse_int(delivered),
                dcr=parse_float(dcr),
                dnr_dpmo=parse_int(dnr_dpmo),
                lor_dpmo=parse_int(lor_dpmo) if lor_dpmo is not None else None,
                pod=parse_float(pod),
                cc=parse_float(cc),
                ce=parse_int(ce),
                dex=parse_float(dex),
            )
            db.add(driver)

        firm_text = ""
        if len(pdf.pages) >= 2:
            firm_text = pdf.pages[1].extract_text()

        kpi_patterns = {
            "dcr": r"Delivery Completion Rate\(DCR\)[\s:]*([\d.,]+)%",
            "dnr_dpmo": r"Delivered Not Received\(DNR DPMO\)[\s:]*([\d.,]+)",
            "lor_dpmo": r"Lost on Road \(LoR\) DPMO[\s:]*([\d.,]+)",
        }

        firm_kpis = {}
        for key, pat in kpi_patterns.items():
            match = re.search(pat, firm_text)
            if match:
                firm_kpis[key] = parse_float(match.group(1))
            else:
                firm_kpis[key] = None

        firm_scorecard = FirmScorecard(
            week=week,
            year=year,
            dcr=firm_kpis["dcr"],
            dnr_dpmo=parse_int(firm_kpis["dnr_dpmo"]) if firm_kpis["dnr_dpmo"] is not None else None,
            lor_dpmo=parse_int(firm_kpis["lor_dpmo"]) if firm_kpis["lor_dpmo"] is not None else None,
        )
        db.add(firm_scorecard)

        db.commit()
        return {"message": f"{len(matches)} Fahrer und Firmen-KPIs für KW {week} erfolgreich gespeichert."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/scorecard/delete_drivers/{week}/{year}")
def delete_scorecard_drivers(week: int, year: int, db: Session = Depends(get_db)):
    deleted_count = db.query(ScorecardDriver).filter_by(week=week, year=year).delete()
    db.commit()
    return {"message": f"{deleted_count} Fahrer-Datensätze für KW {week}/{year} gelöscht."}

class FirmScorecard(Base):
    __tablename__ = "firm_scorecards"

    id = Column(Integer, primary_key=True, index=True)
    week = Column(Integer)
    year = Column(Integer)
    dcr = Column(Float)
    dnr_dpmo = Column(Integer)
    lor_dpmo = Column(Integer)