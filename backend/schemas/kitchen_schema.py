"""Kitchen Request/Response Schemas"""

from pydantic import BaseModel
from typing import Optional


class KitchenStatusUpdateRequest(BaseModel):
	status: str

	class Config:
		json_schema_extra = {
			"example": {
				"status": "Preparing"
			}
		}


class MenuAvailabilityRequest(BaseModel):
	available: bool
	reason: Optional[str] = None

	class Config:
		json_schema_extra = {
			"example": {
				"available": False,
				"reason": "Out of stock"
			}
		}


class KitchenHoursUpdateRequest(BaseModel):
	open_hour: int
	close_hour: int

	class Config:
		json_schema_extra = {
			"example": {
				"open_hour": 9,
				"close_hour": 21
			}
		}


class KitchenToggleRequest(BaseModel):
	force_closed: bool
	apply_to_all_menu: bool = True

	class Config:
		json_schema_extra = {
			"example": {
				"force_closed": True,
				"apply_to_all_menu": True
			}
		}

