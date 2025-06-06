from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    telegram_username = Column(String)
    transporter_id = Column(String, unique=True, nullable=False)
    mentor_first_name = Column(String)
    mentor_last_name = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    days_per_week = Column(Integer, default=5)
    is_flexible = Column(Boolean, default=True)
    prefers_six_days = Column(Boolean, default=False)
    vehicle = Column(String)
    address = Column(String)
    is_active = Column(Boolean, default=True)
    federal_state = Column(String, nullable=True)  # z. B. "BY", "BW", "NRW"

    shifts = relationship("ShiftAssignment", back_populates="employee", cascade="all, delete-orphan")
