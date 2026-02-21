"""Feedback Business Logic Service"""

from sqlalchemy.orm import Session
from loguru import logger

from models.feedback_model import Feedback
from models.order_model import Order
from utils.constants import OrderStatus

from fastapi import HTTPException, status


def submit_feedback(db: Session, order_id: str, engineer_id: str,
					rating: int, comment: str = None) -> Feedback:
	"""Submit feedback for a delivered order"""

	# Verify order exists and is delivered
	order = db.query(Order).filter(Order.order_id == order_id).first()

	if not order:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"code": "ORD_001", "message": "Order not found"}
		)

	if order.engineer_id != engineer_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail={"code": "AUTH_003", "message": "You can only review your own orders"}
		)

	if order.status != OrderStatus.DELIVERED:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"code": "ORD_003", "message": "Can only review delivered orders"}
		)

	# Check if already reviewed
	existing = db.query(Feedback).filter(Feedback.order_id == order_id).first()
	if existing:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"code": "ORD_005", "message": "Feedback already submitted for this order"}
		)

	feedback = Feedback(
		order_id=order_id,
		engineer_id=engineer_id,
		rating=rating,
		comment=comment
	)
	db.add(feedback)
	db.commit()
	db.refresh(feedback)

	logger.info(f"Feedback submitted for order {order_id}: {rating}/5")

	return feedback

