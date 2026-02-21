"""Authentication Request/Response Schemas"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
	email: Optional[str] = None
	employee_id: Optional[str] = None
	password: str

	class Config:
		json_schema_extra = {
			"example": {
				"email": "engineer1@prosensia.com",
				"password": "engineer123"
			}
		}


class RegisterRequest(BaseModel):
	user_id: str
	name: str
	email: EmailStr
	password: str
	role: str
	department: Optional[str] = None
	phone: Optional[str] = None

	class Config:
		json_schema_extra = {
			"example": {
				"user_id": "ENG-011",
				"name": "New Engineer",
				"email": "newengineer@prosensia.com",
				"password": "password123",
				"role": "engineer",
				"department": "Production",
				"phone": "03001234567"
			}
		}


class UpdateUserRequest(BaseModel):
	name: Optional[str] = None
	email: Optional[EmailStr] = None
	password: Optional[str] = None
	role: Optional[str] = None
	department: Optional[str] = None
	phone: Optional[str] = None
	is_active: Optional[bool] = None

	class Config:
		json_schema_extra = {
			"example": {
				"name": "Updated Name",
				"email": "updated@prosensia.com",
				"role": "engineer",
				"department": "Production",
				"phone": "03001234567"
			}
		}


class TokenResponse(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str = "bearer"
	role: str
	user: dict


class RefreshTokenRequest(BaseModel):
	refresh_token: str


class UserResponse(BaseModel):
	user_id: str
	name: str
	email: str
	role: str
	department: Optional[str] = None
	phone: Optional[str] = None
	is_active: bool

