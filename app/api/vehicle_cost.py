from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.vehicle_cost import VehicleCost
from app.models.schemas import VehicleCostCreate, VehicleCostOut
from typing import List
from datetime import datetime, timedelta
from app.utils.date_utils import parse_date


router = APIRouter(prefix="/vehicle-costs", tags=["VehicleCosts"])

@router.post("/", response_model=VehicleCostOut)
def create_vehicle_cost(cost: VehicleCostCreate, db: Session = Depends(get_db)):
    db_cost = VehicleCost(**cost.dict())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost

@router.get("/by-vehicle/{vehicle_id}", response_model=List[VehicleCostOut])
def get_costs_for_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return db.query(VehicleCost).filter(VehicleCost.vehicle_id == vehicle_id).all()

@router.get("/dashboard/{vehicle_id}")
def get_cost_summary(vehicle_id: int, db: Session = Depends(get_db)):
    today = datetime.today().date()
    days_30 = today - timedelta(days=30)
    days_90 = today - timedelta(days=90)

    total_all = db.query(VehicleCost).filter(VehicleCost.vehicle_id == vehicle_id).all()
    total_30 = [c for c in total_all if c.date >= days_30]
    total_90 = [c for c in total_all if c.date >= days_90]

    sum_all = sum(c.amount for c in total_all)
    sum_30 = sum(c.amount for c in total_30)
    sum_90 = sum(c.amount for c in total_90)

    return {
        "total_all": sum_all,
        "last_90_days": sum_90,
        "last_30_days": sum_30
    }

@router.delete("/{cost_id}", status_code=204)
def delete_vehicle_cost(cost_id: int, db: Session = Depends(get_db)):
    cost = db.query(VehicleCost).filter(VehicleCost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Kosten-Eintrag nicht gefunden")
    db.delete(cost)
    db.commit()
    return

from fastapi import UploadFile, File
import openpyxl
import io

@router.post("/upload_excel")
async def upload_vehicle_costs_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    workbook = openpyxl.load_workbook(io.BytesIO(contents))
    sheet = workbook.active

    headers = [cell.value for cell in sheet[1]]
    rows = list(sheet.iter_rows(min_row=2, values_only=True))
    inserted_count = 0

    for row in rows:
        row_data = dict(zip(headers, row))

        try:
            new_cost = VehicleCost(
                vehicle_id=int(row_data["vehicle_id"]),
                date=parse_date(str(row_data["date"])),
                description=row_data.get("description"),
                category=row_data.get("category") or "other",
                amount=float(row_data["amount"])
            )
            db.add(new_cost)
            inserted_count += 1
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Fehler in Zeile {inserted_count + 2}: {e}")

    db.commit()
    return {"message": f"{inserted_count} Kosten erfolgreich importiert."}
from datetime import datetime, date
from typing import Optional

def parse_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unbekanntes Datumsformat: {date_str}")
