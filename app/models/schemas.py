from pydantic import BaseModel, Field
from typing import Optional
import datetime
from enum import Enum

class EmployeeBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_username: Optional[str] = None
    transporter_id: Optional[str] = None
    mentor_first_name: Optional[str] = None
    mentor_last_name: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    days_per_week: Optional[int] = None
    is_flexible: Optional[bool] = None
    prefers_six_days: Optional[bool] = None
    vehicle: Optional[str] = None
    address: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeOut(EmployeeBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class VehicleStatus(str, Enum):
    active = "active"
    in_workshop = "in_workshop"
    defleeted = "defleeted"

class CostCategory(str, Enum):
    maintenance = "maintenance"
    insurance = "insurance"
    fuel = "fuel"
    repair = "repair"
    other = "other"

class FleetVehicleCreate(BaseModel):
    license_plate: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[float] = None
    status: VehicleStatus = VehicleStatus.active

class FleetVehicleUpdate(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[float] = None
    status: Optional[VehicleStatus] = None

class FleetVehicleOut(FleetVehicleCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class VehicleCostCreate(BaseModel):
    vehicle_id: int
    date: datetime.date
    description: Optional[str] = None
    category: CostCategory = CostCategory.other
    amount: float = Field(..., gt=0)

class VehicleCostOut(VehicleCostCreate):
    id: int

    class Config:
        from_attributes = True

class VehicleCostUpdate(BaseModel):
    date: Optional[datetime.date] = None
    description: Optional[str] = None
    category: Optional[CostCategory] = None
    amount: Optional[float] = Field(default=None, gt=0)
import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class ShiftType(str, Enum):
    work = "work"
    free = "free"
    sick = "sick"
    vacation = "vacation"
    appointment = "appointment"

class ShiftAssignmentCreate(BaseModel):
    employee_id: int
    date: datetime.date
    shift_type: ShiftType

class ShiftAssignmentOut(ShiftAssignmentCreate):
    id: int

    class Config:
        from_attributes = True
class EmployeeBase(BaseModel):
    ...
    federal_state: Optional[str] = None
