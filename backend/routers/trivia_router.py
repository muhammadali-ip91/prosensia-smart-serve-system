"""Trivia Game Router"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import get_db
from auth.rbac import require_engineer
from models.user_model import User
from schemas.trivia_schema import TriviaAnswerRequest

from services.trivia_service import get_random_question, submit_answer, get_leaderboard

router = APIRouter()


@router.get("/question")
async def get_question(
    current_user: User = Depends(require_engineer),
    db: Session = Depends(get_db)
):
    """Get a random trivia question"""

    question = get_random_question(db, current_user.user_id)

    if not question:
        return {"message": "No questions available"}

    return question.to_dict()


@router.post("/answer")
async def answer_question(
    request: TriviaAnswerRequest,
    current_user: User = Depends(require_engineer),
    db: Session = Depends(get_db)
):
    """Submit trivia answer"""

    result = submit_answer(
        db=db,
        engineer_id=current_user.user_id,
        question_id=request.question_id,
        selected_option=request.selected_option,
        time_taken=request.time_taken_seconds
    )

    return result


@router.get("/leaderboard")
async def trivia_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_engineer),
    db: Session = Depends(get_db)
):
    """Get weekly trivia leaderboard"""
    return {"leaderboard": get_leaderboard(db, limit)}
