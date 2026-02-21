"""Trivia Question Model - Questions for the engagement module"""

from sqlalchemy import Column, Integer, String, Boolean
from database.connection import Base


class TriviaQuestion(Base):
	__tablename__ = "trivia_questions"

	question_id = Column(Integer, primary_key=True, autoincrement=True)
	question_text = Column(String(500), nullable=False)
	option_a = Column(String(200), nullable=False)
	option_b = Column(String(200), nullable=False)
	option_c = Column(String(200), nullable=False)
	option_d = Column(String(200), nullable=False)
	correct_option = Column(String(1), nullable=False)
	category = Column(String(50), nullable=True)
	difficulty = Column(String(10), nullable=True)
	is_active = Column(Boolean, default=True)

	def __repr__(self):
		return f"<TriviaQuestion {self.question_id}>"

	def to_dict(self):
		return {
			"question_id": self.question_id,
			"question_text": self.question_text,
			"option_a": self.option_a,
			"option_b": self.option_b,
			"option_c": self.option_c,
			"option_d": self.option_d,
			"category": self.category,
			"difficulty": self.difficulty
		}

	def to_dict_with_answer(self):
		data = self.to_dict()
		data["correct_option"] = self.correct_option
		return data

