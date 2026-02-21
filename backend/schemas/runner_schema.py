"""Runner Request/Response Schemas"""

from pydantic import BaseModel
from typing import Optional


class RunnerStatusUpdateRequest(BaseModel):
	status: str

	class Config:
		json_schema_extra = {
			"example": {
				"status": "On The Way"
			}
		}


class RunnerAvailabilityRequest(BaseModel):
	status: str

	class Config:
		json_schema_extra = {
			"example": {
				"status": "Available"
			}
		}


class RunnerResponse(BaseModel):
	runner_id: str
	name: Optional[str] = None
	current_status: str
	active_order_count: int
	max_capacity: int
	total_deliveries: int
	average_delivery_time: float

