from sqlalchemy import Column, Integer, Float
from app.database import Base

class FirmScorecard(Base):
    __tablename__ = "scorecard_firms"

    id = Column(Integer, primary_key=True, index=True)
    week = Column(Integer)
    year = Column(Integer)

    dcr = Column(Float)         # Delivery Completion Rate
    dnr_dpmo = Column(Integer)  # Delivered Not Received (DPMO)
    lor_dpmo = Column(Integer)  # Lost on Road (DPMO)
