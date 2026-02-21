"""Order Request/Response Schemas"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderItemRequest(BaseModel):
	item_id: int
	quantity: int = Field(ge=1, le=10)

	class Config:
		json_schema_extra = {
			"example": {
				"item_id": 1,
				"quantity": 2
			}
		}


class CreateOrderRequest(BaseModel):
	station_id: str
	items: List[OrderItemRequest] = Field(min_length=1)
	priority: str = "Regular"
	special_instructions: Optional[str] = None

	class Config:
		json_schema_extra = {
			"example": {
				"station_id": "Bay-12",
				"items": [
					{"item_id": 1, "quantity": 2},
					{"item_id": 5, "quantity": 1}
				],
				"priority": "Regular",
				"special_instructions": "Less spicy please"
			}
		}


class ModifyOrderRequest(BaseModel):
	items: Optional[List[OrderItemRequest]] = None
	special_instructions: Optional[str] = None
	priority: Optional[str] = None


class OrderItemResponse(BaseModel):
	order_item_id: int
	item_id: int
	quantity: int
	item_price: float
	subtotal: float


class OrderResponse(BaseModel):
	order_id: str
	engineer_id: str
	station_id: str
	priority: str
	status: str
	runner_id: Optional[str] = None
	special_instructions: Optional[str] = None
	total_price: Optional[float] = None
	ai_predicted_eta: Optional[int] = None
	actual_delivery_time: Optional[int] = None
	created_at: str
	items: List[OrderItemResponse] = []


class OrderCreateResponse(BaseModel):
	order_id: str
	status: str
	estimated_wait_time: Optional[int] = None
	eta_confidence: Optional[float] = None
	eta_source: Optional[str] = None
	eta_factors: Optional[dict] = None
	assigned_runner: Optional[str] = None
	total_price: float
	message: str = "Order placed successfully"


class FeedbackRequest(BaseModel):
	rating: int = Field(ge=1, le=5)
	comment: Optional[str] = None

	class Config:
		json_schema_extra = {
			"example": {
				"rating": 4,
				"comment": "Food was delicious!"
			}
		}

