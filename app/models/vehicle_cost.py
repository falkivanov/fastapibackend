from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class CostCategory(str, enum.Enum):
    maintenance = "maintenance"
    insurance = "insurance"
    fuel = "fuel"
    repair = "repair"
    other = "other"

class VehicleCost(Base):
    __tablename__ = "vehicle_costs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("fleet_vehicles.id"), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=True)
    category = Column(Enum(CostCategory), nullable=False, default=CostCategory.other)
    amount = Column(Float, nullable=False)

    vehicle = relationship("FleetVehicle", back_populates="costs")
