"""User Model - All system users (Engineer, Kitchen, Runner, Admin)"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from database.connection import Base


class User(Base):
	__tablename__ = "users"

	user_id = Column(String(20), primary_key=True)
	name = Column(String(100), nullable=False)
	email = Column(String(100), unique=True, nullable=False, index=True)
	password_hash = Column(String(255), nullable=False)
	role = Column(String(20), nullable=False, index=True)
	department = Column(String(50), nullable=True)
	phone = Column(String(15), nullable=True)
	is_active = Column(Boolean, default=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

	def __repr__(self):
		return f"<User {self.user_id} - {self.name} ({self.role})>"

	def to_dict(self):
		return {
			"user_id": self.user_id,
			"name": self.name,
			"email": self.email,
			"role": self.role,
			"department": self.department,
			"phone": self.phone,
			"is_active": self.is_active,
			"created_at": str(self.created_at),
			"updated_at": str(self.updated_at)
		}

