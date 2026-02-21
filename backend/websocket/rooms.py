"""WebSocket Room Management"""


def get_engineer_room(user_id: str) -> str:
    """Get room name for an engineer"""
    return f"engineer_{user_id}"


def get_runner_room(user_id: str) -> str:
    """Get room name for a runner"""
    return f"runner_{user_id}"


def get_kitchen_room() -> str:
    """Get room name for kitchen"""
    return "kitchen"


def get_admin_room() -> str:
    """Get room name for admin"""
    return "admin"


def get_order_room(order_id: str) -> str:
    """Get room name for specific order"""
    return f"order_{order_id}"
