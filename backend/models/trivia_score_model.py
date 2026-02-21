"""Trivia Score Model - Engineer trivia game scores"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base


class TriviaScore(Base):
	__tablename__ = "trivia_scores"

	score_id = Column(Integer, primary_key=True, autoincrement=True)
	engineer_id = Column(String(20), ForeignKey("users.user_id"), nullable=False, index=True)
	question_id = Column(Integer, ForeignKey("trivia_questions.question_id"), nullable=False)
	answered_correctly = Column(Boolean, nullable=False)
	time_taken_seconds = Column(Integer, nullable=True)
	points_earned = Column(Integer, default=0)
	played_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

	def __repr__(self):
		return f"<TriviaScore {self.score_id} - Engineer:{self.engineer_id}>"

	def to_dict(self):
		return {
			"score_id": self.score_id,
			"engineer_id": self.engineer_id,
			"question_id": self.question_id,
			"answered_correctly": self.answered_correctly,
			"time_taken_seconds": self.time_taken_seconds,
			"points_earned": self.points_earned,
			"played_at": str(self.played_at)
		}

