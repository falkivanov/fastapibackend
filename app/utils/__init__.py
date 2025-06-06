from sqlalchemy import Column, Integer, Float
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import pdfplumber
import re
import io

from app.database import get_db, Base
from app.models.scorecard_driver import ScorecardDriver
from app.models.employee import Employee
from app.models.firm_scorecard import FirmScorecard

router = APIRouter()

# Rest des Codes bleibt unverändert