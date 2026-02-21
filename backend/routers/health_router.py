"""System Health Check Router"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import redis
import time

from database.session import get_db
from config import settings
from services.eta_service import eta_service

router = APIRouter()
APP_START_TS = time.time()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """System health check"""

    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": settings.APP_VERSION,
        "checks": {}
    }

    # Database check
    try:
        db.execute(text("SELECT 1"))
        health["checks"]["database"] = "connected"
    except Exception:
        health["checks"]["database"] = "disconnected"
        health["status"] = "unhealthy"

    # Redis check (optional in local/perf mode)
    if settings.HEALTH_CHECK_REDIS:
        try:
            redis_client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
            redis_client.ping()
            health["checks"]["redis"] = "connected"
        except Exception:
            health["checks"]["redis"] = "disconnected"
            if settings.HEALTH_CHECK_STRICT:
                health["status"] = "unhealthy"
    else:
        health["checks"]["redis"] = "skipped"

    # AI Model check
    health["checks"]["ai_model"] = "loaded" if eta_service.model_loaded else "not_loaded"

    if eta_service.metadata:
        health["checks"]["ai_model_accuracy"] = eta_service.metadata.get("metrics", {}).get("mae")

    uptime_seconds = int(time.time() - APP_START_TS)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    health["checks"]["uptime_seconds"] = uptime_seconds
    health["checks"]["uptime"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return health
