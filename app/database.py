import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

# Logger konfigurieren
logger = logging.getLogger(__name__)

# Datenbank-URL aus Umgebungsvariablen lesen
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fastapi_db"
)

# Engine mit Connection Pooling konfigurieren
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,  # Maximale Anzahl der Verbindungen im Pool
    max_overflow=10,  # Maximale Anzahl der zusätzlichen Verbindungen
    pool_timeout=30,  # Timeout für das Warten auf eine Verbindung
    pool_recycle=1800,  # Verbindungen nach 30 Minuten recyceln
    pool_pre_ping=True,  # Verbindungen vor der Verwendung testen
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"  # SQL-Logging aktivieren
)

# Session Factory mit optimierten Einstellungen
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Verhindert das Ablaufen der Objekte nach dem Commit
)

Base = declarative_base()

@contextmanager
def get_db():
    """
    Kontext-Manager für Datenbankverbindungen mit automatischer Fehlerbehandlung
    und Ressourcenbereinigung.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Datenbankfehler: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialisiert die Datenbank und erstellt alle Tabellen.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Datenbank erfolgreich initialisiert")
    except Exception as e:
        logger.error(f"Fehler bei der Datenbankinitialisierung: {str(e)}")
        raise
