import logging
from logging.handlers import RotatingFileHandler
import sys
from app.config import get_settings

settings = get_settings()

def setup_logging():
    """
    Konfiguriert das Logging-System mit Rotation und verschiedenen Handlern.
    """
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # Format für die Logs
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler mit Rotation
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # SQLAlchemy Logger konfigurieren
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    if settings.SQL_ECHO:
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger.setLevel(logging.WARNING)

    # FastAPI Logger konfigurieren
    fastapi_logger = logging.getLogger('fastapi')
    fastapi_logger.setLevel(settings.LOG_LEVEL)

    return root_logger 