"""
Application Configuration
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
	"""Application settings loaded from environment"""

	# -------- APP --------
	APP_NAME: str = "ProSensia Smart-Serve"
	APP_VERSION: str = "2.0.0"
	DEBUG: bool = True
	APP_HOST: str = "0.0.0.0"
	APP_PORT: int = 8000

	# -------- DATABASE --------
	DATABASE_URL: str = "postgresql://prosensia_user:prosensia_pass@localhost:5432/prosensia_db"
	DB_POOL_SIZE: int = 5
	DB_MAX_OVERFLOW: int = 5
	DB_POOL_TIMEOUT: int = 15
	DB_POOL_RECYCLE: int = 1800
	DB_POOL_PRE_PING: bool = True

	# -------- REDIS --------
	REDIS_URL: str = "redis://localhost:6379/0"

	# -------- SOCKET.IO SCALING --------
	SOCKETIO_USE_REDIS_MANAGER: bool = False
	SOCKETIO_REDIS_CHANNEL: str = "prosensia_socketio"
	SOCKETIO_PING_INTERVAL: int = 25
	SOCKETIO_PING_TIMEOUT: int = 60
	SOCKETIO_MAX_HTTP_BUFFER_SIZE: int = 1000000

	# -------- JWT --------
	JWT_SECRET_KEY: str = "prosensia-dev-secret-key-2024"
	JWT_ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
	REFRESH_TOKEN_EXPIRE_DAYS: int = 7

	# -------- CORS --------
	FRONTEND_URL: str = "http://localhost:3000"
	CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

	# -------- AI MODEL --------
	AI_MODEL_PATH: str = "ai_module/models/eta_model.pkl"
	AI_FALLBACK_ENABLED: bool = True
	AI_RETRAIN_THRESHOLD_MAE: float = 3.0

	# -------- RATE LIMITING --------
	RATE_LIMIT_PER_MINUTE: int = 100
	LOGIN_RATE_LIMIT_PER_15MIN: int = 10

	# -------- PERFORMANCE --------
	ENABLE_REQUEST_LOGGING: bool = True
	HEALTH_CHECK_REDIS: bool = False
	HEALTH_CHECK_STRICT: bool = False

	@property
	def cors_origins_list(self) -> List[str]:
		"""Convert comma-separated CORS origins to list"""
		return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

	class Config:
		env_file = ".env"
		case_sensitive = True
		extra = "ignore"


# Create global settings instance
settings = Settings()

