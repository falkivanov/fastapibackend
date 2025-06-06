from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.shift import ShiftAssignment
from app.models.schemas import ShiftAssignmentCreate, ShiftAssignmentOut
from typing import List
import datetime
import holidays
feiertage = holidays.Germany(prov="BY")  # oder je nach Bundesland


router = APIRouter(prefix="/shifts", tags=["Shift Planning"])

@router.post("/", response_model=ShiftAssignmentOut)
def assign_shift(shift: ShiftAssignmentCreate, db: Session = Depends(get_db)):
    assignment = ShiftAssignment(**shift.dict())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

@router.get("/by-week/{week_start}", response_model=List[ShiftAssignmentOut])
def get_week_shifts(week_start: datetime.date, db: Session = Depends(get_db)):
    week_end = week_start + datetime.timedelta(days=6)
    return db.query(ShiftAssignment).filter(
        ShiftAssignment.date >= week_start,
        ShiftAssignment.date <= week_end
    ).all()

@router.delete("/{assignment_id}", status_code=204)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    shift = db.query(ShiftAssignment).filter(ShiftAssignment.id == assignment_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Schicht nicht gefunden")
    db.delete(shift)
    db.commit()

@router.post("/auto-plan/{week_start}")
def auto_plan_week(week_start: datetime.date, mode: str = "forecast", db: Session = Depends(get_db)):
    from app.models.employee import Employee

    # 1. Daten vorbereiten
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    week_end = week_start + datetime.timedelta(days=6)

    # 2. Plan initialisieren
    schedule = {day: [] for day in range(7)}  # Mo–So

    # 3. Forecast-Planung: Bevorzugte Tage zuerst
    for emp in employees:
        assigned = 0
        preferred = emp.preferred_days or []

        for offset in range(7):
            day_date = week_start + datetime.timedelta(days=offset)
            weekday = day_date.weekday()

            # 3a. Bevorzugte Tage
            if weekday in preferred and assigned < emp.days_per_week:
                db.add(ShiftAssignment(
                    employee_id=emp.id,
                    date=day_date,
                    shift_type="work"
                ))
                assigned += 1

        # 4. Maximum-Modus: auch flexible Tage zulassen
        if mode == "maximum" and emp.is_flexible and assigned < emp.days_per_week:
            for offset in range(7):
                day_date = week_start + datetime.timedelta(days=offset)
                weekday = day_date.weekday()

                if weekday not in preferred and assigned < emp.days_per_week:
                    db.add(ShiftAssignment(
                        employee_id=emp.id,
                        date=day_date,
                        shift_type="work"
                    ))
                    assigned += 1

    db.commit()
    return {"message": f"Auto-Plan für Woche ab {week_start} im Modus '{mode}' abgeschlossen."}
@router.post("/auto-plan/{week_start}")
def auto_plan_week(
    week_start: datetime.date,
    mode: str = "forecast",
    db: Session = Depends(get_db)
):
    from app.models.employee import Employee
    from app.models.shift import ShiftAssignment

    today = datetime.date.today()
    week_end = week_start + datetime.timedelta(days=6)

    # Vorherige Zuweisungen dieser Woche abrufen
    existing = db.query(ShiftAssignment).filter(
        ShiftAssignment.date >= week_start,
        ShiftAssignment.date <= week_end
    ).all()
    existing_map = {(e.employee_id, e.date): e for e in existing}

    employees = db.query(Employee).filter(Employee.is_active == True).all()

    for emp in employees:
        if not emp.federal_state:
            continue  # ❌ Bundesland nicht gesetzt – überspringen

        # Individuelle Feiertage
        feiertage = holidays.Germany(prov=emp.federal_state, years=week_start.year)
        assigned_days = 0
        preferred = emp.preferred_days or []

        for offset in range(7):
            day_date = week_start + datetime.timedelta(days=offset)
            weekday = day_date.weekday()

            # 🔒 Validierungen
            if day_date < today:
                continue
            if (emp.id, day_date) in existing_map:
                continue
            if day_date in feiertage:
                continue
            if assigned_days >= emp.days_per_week:
                continue
            if mode == "forecast" and weekday not in preferred and not emp.is_flexible:
                continue

            # ✅ Zuweisung speichern
            db.add(ShiftAssignment(
                employee_id=emp.id,
                date=day_date,
                shift_type="work"
            ))
            assigned_days += 1

    db.commit()
    return {"message": f"Auto-Planung für {week_start} – {week_end} im Modus '{mode}' abgeschlossen."}