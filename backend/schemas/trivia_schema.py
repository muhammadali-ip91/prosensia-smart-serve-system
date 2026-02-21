"""Trivia Schemas"""

from pydantic import BaseModel, Field
from typing import Optional


class TriviaQuestionResponse(BaseModel):
	question_id: int
	question_text: str
	option_a: str
	option_b: str
	option_c: str
	option_d: str
	category: Optional[str] = None
	difficulty: Optional[str] = None


class TriviaAnswerRequest(BaseModel):
	question_id: int
	selected_option: str = Field(pattern="^[ABCD]$")
	time_taken_seconds: int = Field(ge=0, le=60)

	class Config:
		json_schema_extra = {
			"example": {
				"question_id": 1,
				"selected_option": "A",
				"time_taken_seconds": 8
			}
		}


class TriviaAnswerResponse(BaseModel):
	correct: bool
	correct_option: str
	points_earned: int
	total_score: int


class LeaderboardEntry(BaseModel):
	rank: int
	engineer_id: str
	engineer_name: str
	total_points: int
	questions_answered: int
	accuracy: float

