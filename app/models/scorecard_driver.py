from sqlalchemy import Column, Integer, Float, String
from app.database import Base  # <- sicherstellen, dass das importiert ist

class ScorecardDriver(Base):
    __tablename__ = "scorecard_drivers"

    id = Column(Integer, primary_key=True, index=True)
    week = Column(Integer)
    year = Column(Integer)
    name = Column(String)
    delivered = Column(Integer)
    dcr = Column(Float)
    dnr_dpmo = Column(Integer)
    lor_dpmo = Column(Integer)  # <- NEU
    pod = Column(Float)
    cc = Column(Float)
    ce = Column(Integer)
    dex = Column(Float)  # Wird auch für "CDF" genutzt
