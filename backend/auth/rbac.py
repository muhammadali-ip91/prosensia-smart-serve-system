"""Role-Based Access Control"""

from fastapi import HTTPException, status, Depends
from functools import wraps
from typing import List

from auth.dependencies import get_current_user
from models.user_model import User


class RoleChecker:
	"""
	Dependency class to check user roles.
    
	Usage:
		@router.get("/admin-only")
		async def admin_endpoint(user: User = Depends(RoleChecker(["admin"]))):
			...
	"""

	def __init__(self, allowed_roles: List[str]):
		self.allowed_roles = allowed_roles

	async def __call__(self, user: User = Depends(get_current_user)) -> User:
		if user.role not in self.allowed_roles:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail={
					"code": "AUTH_003",
					"message": f"Access denied. Required role: {', '.join(self.allowed_roles)}. "
							   f"Your role: {user.role}"
				}
			)
		return user


# Pre-built role checkers for convenience
require_admin = RoleChecker(["admin"])
require_kitchen = RoleChecker(["kitchen", "admin"])
require_runner = RoleChecker(["runner", "admin"])
require_engineer = RoleChecker(["engineer", "admin"])
require_any_authenticated = RoleChecker(["engineer", "kitchen", "runner", "admin"])


ROLE_PERMISSIONS = {
	"engineer": {
		"place_order",
		"cancel_order",
		"view_own_orders",
		"submit_feedback",
	},
	"kitchen": {
		"view_kitchen_orders",
		"update_kitchen_status",
		"manage_availability",
	},
	"runner": {
		"view_assigned_deliveries",
		"update_delivery",
		"update_runner_status",
	},
	"admin": {
		"place_order",
		"cancel_order",
		"view_own_orders",
		"submit_feedback",
		"view_kitchen_orders",
		"update_kitchen_status",
		"manage_availability",
		"view_assigned_deliveries",
		"update_delivery",
		"update_runner_status",
		"manage_menu",
		"manage_users",
		"view_reports",
	},
}


def check_role_permission(role: str, permission: str) -> bool:
	"""Check if role has a specific permission."""
	if role not in ROLE_PERMISSIONS:
		return False
	return permission in ROLE_PERMISSIONS[role]

