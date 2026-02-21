"""Application Constants"""


# ============================================
# ORDER STATUS
# ============================================
class OrderStatus:
	PLACED = "Placed"
	CONFIRMED = "Confirmed"
	PREPARING = "Preparing"
	READY = "Ready"
	PICKED_UP = "PickedUp"
	ON_THE_WAY = "OnTheWay"
	DELIVERED = "Delivered"
	CANCELLED = "Cancelled"
	REJECTED = "Rejected"
	DELAYED = "Delayed"

	ALL = [PLACED, CONFIRMED, PREPARING, READY, PICKED_UP,
		   ON_THE_WAY, DELIVERED, CANCELLED, REJECTED, DELAYED]

	ACTIVE = [PLACED, CONFIRMED, PREPARING, READY, PICKED_UP, ON_THE_WAY]
	TERMINAL = [DELIVERED, CANCELLED, REJECTED]
	CANCELLABLE = [PLACED, CONFIRMED]


# ============================================
# ORDER STATUS TRANSITIONS (who can change what)
# ============================================
STATUS_TRANSITIONS = {
	OrderStatus.PLACED: {
		"allowed_next": [
			OrderStatus.CONFIRMED,
			OrderStatus.PREPARING,
			OrderStatus.CANCELLED,
			OrderStatus.REJECTED,
		],
		"allowed_roles": ["system", "engineer", "kitchen", "admin"]
	},
	OrderStatus.CONFIRMED: {
		"allowed_next": [OrderStatus.PREPARING, OrderStatus.CANCELLED],
		"allowed_roles": ["kitchen", "engineer", "admin"]
	},
	OrderStatus.PREPARING: {
		"allowed_next": [OrderStatus.READY, OrderStatus.DELAYED],
		"allowed_roles": ["kitchen", "admin"]
	},
	OrderStatus.READY: {
		"allowed_next": [OrderStatus.PICKED_UP],
		"allowed_roles": ["runner", "admin"]
	},
	OrderStatus.PICKED_UP: {
		"allowed_next": [OrderStatus.ON_THE_WAY],
		"allowed_roles": ["runner", "admin"]
	},
	OrderStatus.ON_THE_WAY: {
		"allowed_next": [OrderStatus.DELIVERED, OrderStatus.DELAYED],
		"allowed_roles": ["runner", "admin"]
	},
}


# ============================================
# RUNNER STATUS
# ============================================
class RunnerStatus:
	AVAILABLE = "Available"
	BUSY = "Busy"
	OFFLINE = "Offline"

	ALL = [AVAILABLE, BUSY, OFFLINE]


# ============================================
# USER ROLES
# ============================================
class UserRole:
	ENGINEER = "engineer"
	KITCHEN = "kitchen"
	RUNNER = "runner"
	ADMIN = "admin"

	ALL = [ENGINEER, KITCHEN, RUNNER, ADMIN]


# ============================================
# PRIORITY
# ============================================
class Priority:
	REGULAR = "Regular"
	URGENT = "Urgent"

	ALL = [REGULAR, URGENT]


# ============================================
# PEAK HOURS
# ============================================
PEAK_HOURS = [(12, 14), (18, 20)]  # Lunch and Dinner
KITCHEN_OPEN_HOUR = 9
KITCHEN_CLOSE_HOUR = 21


# ============================================
# TRIVIA
# ============================================
TRIVIA_TIME_LIMIT_SECONDS = 15
TRIVIA_POINTS_CORRECT = 10
TRIVIA_POINTS_FAST_BONUS = 5  # If answered in < 5 seconds

