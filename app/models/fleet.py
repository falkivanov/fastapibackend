from sqlalchemy import Column, Integer, String, Boolean, Float, Enum
from app.database import Base
import enum

class VehicleStatus(str, enum.Enum):
    active = "active"
    in_workshop = "in_workshop"
    defleeted = "defleeted"

class FleetVehicle(Base):
    __tablename__ = "fleet_vehicles"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, nullable=False)
    manufacturer = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Float)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.active)
    is_active = Column(Boolean, default=True)
from sqlalchemy.orm import relationship

# Innerhalb der FleetVehicle-Klasse
costs = relationship("VehicleCost", back_populates="vehicle", cascade="all, delete-orphan")
