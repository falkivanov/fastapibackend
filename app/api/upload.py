from fastapi import APIRouter, UploadFile, File
import shutil
from pathlib import Path
from app.services.scorecard_service import (
    extract_scorecard_data,
    extract_firm_kpis_from_pdf,
    extract_kw_from_filename,
)

router = APIRouter()

UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload/{category}")
async def upload_file(category: str, file: UploadFile = File(...)):
    temp_path = UPLOAD_DIR / file.filename

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if category.lower() == "scorecard":
        # Basisdaten aus erster Seite
        core_data = extract_scorecard_data(temp_path)

        # KW aus Dateinamen ziehen
        core_data["kw"] = extract_kw_from_filename(file.filename)

        # Firm KPIs aus Seite 2
        core_data["firm_kpis"] = extract_firm_kpis_from_pdf(temp_path)

        return core_data

    return {"filename": file.filename, "category": category}
