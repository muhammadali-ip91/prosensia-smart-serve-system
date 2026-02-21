"""Notification Business Logic Service"""

from sqlalchemy.orm import Session
from typing import Optional, List
from loguru import logger

from models.notification_model import Notification
from models.user_model import User


def create_notification(db: Session, user_id: Optional[str],
						notification_type: str, title: str,
						message: str, priority: str = "normal",
						action_url: str = None,
						role_target: str = None) -> Notification:
	"""Create a notification"""

	if user_id:
		# Single user notification
		notif = Notification(
			user_id=user_id,
			type=notification_type,
			title=title,
			message=message,
			priority=priority,
			action_url=action_url
		)
		db.add(notif)
		db.flush()
		return notif

	elif role_target:
		# Notify all users with a specific role
		users = db.query(User).filter(
			User.role == role_target,
			User.is_active == True
		).all()

		notifications = []
		for user in users:
			notif = Notification(
				user_id=user.user_id,
				type=notification_type,
				title=title,
				message=message,
				priority=priority,
				action_url=action_url
			)
			db.add(notif)
			notifications.append(notif)

		db.flush()

		logger.info(f"Notification sent to {len(notifications)} {role_target} users")
		return notifications[0] if notifications else None


def get_user_notifications(db: Session, user_id: str,
						   unread_only: bool = False,
						   limit: int = 50) -> List[Notification]:
	"""Get notifications for a user"""

	query = db.query(Notification).filter(
		Notification.user_id == user_id
	)

	if unread_only:
		query = query.filter(Notification.is_read == False)

	return query.order_by(
		Notification.created_at.desc()
	).limit(limit).all()


def mark_notifications_read(db: Session, user_id: str,
							notification_ids: List[int]) -> int:
	"""Mark notifications as read"""

	count = db.query(Notification).filter(
		Notification.user_id == user_id,
		Notification.notification_id.in_(notification_ids)
	).update(
		{"is_read": True},
		synchronize_session=False
	)

	db.commit()
	return count


def get_unread_count(db: Session, user_id: str) -> int:
	"""Get count of unread notifications"""

	return db.query(Notification).filter(
		Notification.user_id == user_id,
		Notification.is_read == False
	).count()

