"""Trivia Game Business Logic Service"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, Integer
from typing import List
from loguru import logger
from datetime import datetime, timedelta

from models.trivia_question_model import TriviaQuestion
from models.trivia_score_model import TriviaScore
from models.user_model import User
from utils.constants import TRIVIA_POINTS_CORRECT, TRIVIA_POINTS_FAST_BONUS


def get_random_question(db: Session, engineer_id: str) -> TriviaQuestion:
	"""Get a random trivia question not recently answered"""

	# Get recently answered question IDs
	recent = db.query(TriviaScore.question_id).filter(
		TriviaScore.engineer_id == engineer_id,
		TriviaScore.played_at > datetime.utcnow() - timedelta(hours=1)
	).all()
	recent_ids = [r[0] for r in recent]

	# Get random question not in recent
	query = db.query(TriviaQuestion).filter(
		TriviaQuestion.is_active == True
	)

	if recent_ids:
		query = query.filter(TriviaQuestion.question_id.notin_(recent_ids))

	question = query.order_by(func.random()).first()

	# If all questions exhausted, get any random
	if not question:
		question = db.query(TriviaQuestion).filter(
			TriviaQuestion.is_active == True
		).order_by(func.random()).first()

	return question


def submit_answer(db: Session, engineer_id: str, question_id: int,
				  selected_option: str, time_taken: int) -> dict:
	"""Submit trivia answer and calculate score"""

	question = db.query(TriviaQuestion).filter(
		TriviaQuestion.question_id == question_id
	).first()

	if not question:
		return {"error": "Question not found"}

	is_correct = selected_option.upper() == question.correct_option.upper()

	# Calculate points
	points = 0
	if is_correct:
		points = TRIVIA_POINTS_CORRECT
		if time_taken < 5:
			points += TRIVIA_POINTS_FAST_BONUS  # Speed bonus

	# Save score
	score = TriviaScore(
		engineer_id=engineer_id,
		question_id=question_id,
		answered_correctly=is_correct,
		time_taken_seconds=time_taken,
		points_earned=points
	)
	db.add(score)
	db.commit()

	# Get total score
	total = db.query(func.sum(TriviaScore.points_earned)).filter(
		TriviaScore.engineer_id == engineer_id,
		TriviaScore.played_at > datetime.utcnow() - timedelta(days=7)
	).scalar() or 0

	return {
		"correct": is_correct,
		"correct_option": question.correct_option,
		"points_earned": points,
		"total_score": total
	}


def get_leaderboard(db: Session, limit: int = 10) -> List[dict]:
	"""Get weekly trivia leaderboard"""

	week_ago = datetime.utcnow() - timedelta(days=7)

	results = db.query(
		TriviaScore.engineer_id,
		func.sum(TriviaScore.points_earned).label("total_points"),
		func.count(TriviaScore.score_id).label("questions_answered"),
		func.sum(
			func.cast(TriviaScore.answered_correctly, Integer)
		).label("correct_answers")
	).filter(
		TriviaScore.played_at > week_ago
	).group_by(
		TriviaScore.engineer_id
	).order_by(
		desc("total_points")
	).limit(limit).all()

	leaderboard = []
	for rank, row in enumerate(results, 1):
		user = db.query(User).filter(User.user_id == row.engineer_id).first()
		accuracy = (row.correct_answers / max(row.questions_answered, 1)) * 100

		leaderboard.append({
			"rank": rank,
			"engineer_id": row.engineer_id,
			"engineer_name": user.name if user else "Unknown",
			"total_points": row.total_points,
			"questions_answered": row.questions_answered,
			"accuracy": round(accuracy, 1)
		})

	return leaderboard

