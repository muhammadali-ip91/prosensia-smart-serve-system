"""System Log Model - Application logs stored in database"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database.connection import Base


class SystemLog(Base):
	__tablename__ = "system_logs"

	log_id = Column(Integer, primary_key=True, autoincrement=True)
	log_level = Column(String(10), nullable=False, index=True)
	module = Column(String(50), nullable=False, index=True)
	message = Column(String(1000), nullable=False)
	user_id = Column(String(20), nullable=True)
	request_path = Column(String(200), nullable=True)
	response_code = Column(Integer, nullable=True)
	response_time_ms = Column(Integer, nullable=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

	def __repr__(self):
		return f"<SystemLog {self.log_id} - [{self.log_level}] {self.module}>"

	def to_dict(self):
		return {
			"log_id": self.log_id,
			"log_level": self.log_level,
			"module": self.module,
			"message": self.message,
			"user_id": self.user_id,
			"request_path": self.request_path,
			"response_code": self.response_code,
			"response_time_ms": self.response_time_ms,
			"created_at": str(self.created_at)
		}

