"""Station Model - Factory workstations"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from database.connection import Base


class Station(Base):
	__tablename__ = "stations"

	station_id = Column(String(20), primary_key=True)
	station_name = Column(String(50), nullable=False)
	floor = Column(Integer, nullable=False)
	building = Column(String(50), nullable=False)
	distance_from_kitchen = Column(Integer, nullable=False)
	qr_token = Column(String(255), nullable=False)
	qr_token_expires_at = Column(DateTime(timezone=True), nullable=False)
	is_active = Column(Boolean, default=True)

	def __repr__(self):
		return f"<Station {self.station_id} - {self.station_name}>"

	def to_dict(self):
		return {
			"station_id": self.station_id,
			"station_name": self.station_name,
			"floor": self.floor,
			"building": self.building,
			"distance_from_kitchen": self.distance_from_kitchen,
			"is_active": self.is_active
		}

