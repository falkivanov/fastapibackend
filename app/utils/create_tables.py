from app.database import Base, engine
from app.models.scorecard_driver import ScorecardDriver
from app.models.employee import Employee

print("Erzeuge Tabellen ...")
Base.metadata.drop_all(bind=engine)  # optional, um alte zu löschen
Base.metadata.create_all(bind=engine)
print("Tabellen wurden erfolgreich erstellt.")
from app.models.firm_scorecard import FirmScorecard  # NEU hinzufügen
from app.models import fleet, vehicle_cost
Base.metadata.create_all(bind=engine)
