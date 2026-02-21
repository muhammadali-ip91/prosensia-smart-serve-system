"""
Database Session Manager
Provides database session for each request
"""

from database.connection import SessionLocal
from loguru import logger


def get_db():
	"""
	Dependency that provides a database session.
	Used in FastAPI endpoints:
    
	@app.get("/example")
	def example(db: Session = Depends(get_db)):
		...
	"""
	db = SessionLocal()
	try:
		yield db
	except Exception as e:
		logger.error(f"Database session error: {e}")
		db.rollback()
		raise
	finally:
		db.close()

