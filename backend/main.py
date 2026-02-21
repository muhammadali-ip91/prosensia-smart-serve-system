"""
ProSensia Smart-Serve - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
	sys.path.insert(0, CURRENT_DIR)

from config import settings
from database.connection import engine, create_tables
from database.session import get_db

# Import routers
from routers.auth_router import router as auth_router
from routers.order_router import router as order_router
from routers.menu_router import router as menu_router
from routers.kitchen_router import router as kitchen_router
from routers.runner_router import router as runner_router
from routers.admin_router import router as admin_router
from routers.notification_router import router as notification_router
from routers.trivia_router import router as trivia_router
from routers.health_router import router as health_router

# Import middleware
from middleware.error_handler import add_error_handlers
from middleware.logging_middleware import LoggingMiddleware
from middleware.rate_limiter import limiter

# Import WebSocket
from websocket.socket_manager import create_socket_app

# Import Loguru
from loguru import logger


# ============================================
# LIFESPAN (Startup & Shutdown)
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Runs on startup and shutdown"""

	# -------- STARTUP --------
	logger.info("🚀 Starting ProSensia Smart-Serve...")

	# Create database tables
	create_tables()
	logger.info("✅ Database tables created")

	# Load AI model
	try:
		from services.eta_service import eta_service
		eta_service.load_model()
		logger.info("✅ AI Model loaded")
	except Exception as e:
		logger.warning(f"⚠️ AI Model failed to load: {e}")
		logger.warning("   System will use fallback predictions")

	logger.info(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} is ready!")
	logger.info(f"📄 API Docs: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")

	yield

	# -------- SHUTDOWN --------
	logger.info("🛑 Shutting down ProSensia Smart-Serve...")


# ============================================
# CREATE APP
# ============================================
app = FastAPI(
	title=settings.APP_NAME,
	version=settings.APP_VERSION,
	description="Smart Food Delivery Management System for Industrial Environments",
	docs_url="/docs",
	redoc_url="/redoc",
	lifespan=lifespan
)

uploads_dir = Path(__file__).resolve().parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


# ============================================
# MIDDLEWARE
# ============================================

# CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins_list,
	allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Logging
app.add_middleware(LoggingMiddleware)

# Error Handlers
add_error_handlers(app)

# Rate Limiting
app.state.limiter = limiter


# ============================================
# REGISTER ROUTERS
# ============================================
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
app.include_router(menu_router, prefix="/menu", tags=["Menu"])
app.include_router(kitchen_router, prefix="/kitchen", tags=["Kitchen"])
app.include_router(runner_router, prefix="/runner", tags=["Runner"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(notification_router, prefix="/notifications", tags=["Notifications"])
app.include_router(trivia_router, prefix="/trivia", tags=["Trivia"])
app.include_router(health_router, tags=["System"])


# ============================================
# WEBSOCKET (Socket.IO)
# ============================================
socket_app = create_socket_app(app)


# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
async def root():
	return {
		"name": settings.APP_NAME,
		"version": settings.APP_VERSION,
		"status": "running",
		"docs": "/docs"
	}


# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"main:socket_app",
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		reload=settings.DEBUG
	)

