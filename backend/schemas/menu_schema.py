"""Menu Request/Response Schemas"""

from pydantic import BaseModel
from typing import List, Optional


class MenuItemResponse(BaseModel):
	item_id: int
	item_name: str
	category: str
	price: float
	prep_time_estimate: int
	image_url: Optional[str] = None
	is_available: bool
	unavailable_reason: Optional[str] = None


class MenuCategoryResponse(BaseModel):
	category: str
	items: List[MenuItemResponse]


class MenuResponse(BaseModel):
	categories: List[MenuCategoryResponse]
	total_items: int


class CreateMenuItemRequest(BaseModel):
	item_name: str
	category: str
	price: float
	prep_time_estimate: int
	complexity_score: int = 1
	image_url: Optional[str] = None
	is_available: bool = True
	unavailable_reason: Optional[str] = None

	class Config:
		json_schema_extra = {
			"example": {
				"item_name": "Chicken Burger",
				"category": "Snacks",
				"price": 200.00,
				"prep_time_estimate": 12,
				"complexity_score": 2
			}
		}


class UpdateMenuItemRequest(BaseModel):
	item_name: Optional[str] = None
	category: Optional[str] = None
	price: Optional[float] = None
	prep_time_estimate: Optional[int] = None
	complexity_score: Optional[int] = None
	image_url: Optional[str] = None
	is_available: Optional[bool] = None
	unavailable_reason: Optional[str] = None

