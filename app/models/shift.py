# app/models/shift.py
from sqlalchemy import Column, Integer, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ShiftType(str, enum.Enum):
    work = "work"
    free = "free"
    sick = "sick"
    vacation = "vacation"
    appointment = "appointment"

class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    shift_type = Column(Enum(ShiftType), nullable=False)

    employee = relationship("Employee", back_populates="shifts")
