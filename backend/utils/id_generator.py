"""ID Generation Utilities"""

from datetime import datetime
from sqlalchemy.orm import Session
from models.order_model import Order


def generate_order_id(db: Session) -> str:
	"""
	Generate unique order ID.
	Format: ORD-YYYY-NNNN
	Example: ORD-2024-0001
	"""

	year = datetime.now().strftime("%Y")
	prefix = f"ORD-{year}-"

	# Get last order number for this year
	last_order = (
		db.query(Order)
		.filter(Order.order_id.like(f"{prefix}%"))
		.order_by(Order.order_id.desc())
		.first()
	)

	if last_order:
		last_num = int(last_order.order_id.split("-")[-1])
		new_num = last_num + 1
	else:
		new_num = 1

	return f"{prefix}{new_num:04d}"

