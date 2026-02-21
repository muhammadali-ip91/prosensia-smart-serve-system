"""
Database Connection Setup
PostgreSQL connection using SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
from loguru import logger
from pathlib import Path


def _normalize_database_url(database_url: str) -> str:
	if not database_url.startswith("sqlite:///"):
		return database_url

	sqlite_path = database_url[len("sqlite:///"):]
	if sqlite_path == ":memory:":
		return database_url

	if len(sqlite_path) > 1 and sqlite_path[1] == ":":
		return f"sqlite:///{Path(sqlite_path).as_posix()}"

	if sqlite_path.startswith("/"):
		return f"sqlite:///{Path(sqlite_path).as_posix()}"

	backend_root = Path(__file__).resolve().parent.parent
	abs_path = (backend_root / sqlite_path).resolve()
	return f"sqlite:///{abs_path.as_posix()}"

# ============================================
# DATABASE ENGINE
# ============================================
resolved_database_url = _normalize_database_url(settings.DATABASE_URL)

if resolved_database_url != settings.DATABASE_URL:
	logger.info(f"Using normalized DATABASE_URL: {resolved_database_url}")

engine = create_engine(
	resolved_database_url,
	pool_size=settings.DB_POOL_SIZE,
	max_overflow=settings.DB_MAX_OVERFLOW,
	pool_timeout=settings.DB_POOL_TIMEOUT,
	pool_recycle=settings.DB_POOL_RECYCLE,
	pool_pre_ping=settings.DB_POOL_PRE_PING,
	echo=settings.DEBUG
)

# ============================================
# SESSION FACTORY
# ============================================
SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine
)

# ============================================
# BASE CLASS FOR MODELS
# ============================================
Base = declarative_base()


# ============================================
# CREATE ALL TABLES
# ============================================
def create_tables():
	"""Create all database tables"""
	try:
		# Import all models so Base knows about them
		from models import user_model
		from models import station_model
		from models import menu_item_model
		from models import order_model
		from models import order_item_model
		from models import runner_model
		from models import order_status_history_model
		from models import feedback_model
		from models import notification_model
		from models import trivia_question_model
		from models import trivia_score_model
		from models import ai_training_data_model
		from models import system_log_model
		from models import kitchen_settings_model

		Base.metadata.create_all(bind=engine)
		logger.info("✅ All database tables created successfully")
	except Exception as e:
		logger.error(f"❌ Failed to create tables: {e}")
		raise

