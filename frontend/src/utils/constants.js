// Order Statuses
export const ORDER_STATUS = {
	PLACED: 'Placed',
	CONFIRMED: 'Confirmed',
	PREPARING: 'Preparing',
	READY: 'Ready',
	PICKED_UP: 'PickedUp',
	ON_THE_WAY: 'OnTheWay',
	DELIVERED: 'Delivered',
	CANCELLED: 'Cancelled',
	REJECTED: 'Rejected',
	DELAYED: 'Delayed',
}

// Status Flow for Progress Bar
export const STATUS_FLOW = [
	ORDER_STATUS.PLACED,
	ORDER_STATUS.CONFIRMED,
	ORDER_STATUS.PREPARING,
	ORDER_STATUS.READY,
	ORDER_STATUS.PICKED_UP,
	ORDER_STATUS.ON_THE_WAY,
	ORDER_STATUS.DELIVERED,
]

// Status Colors
export const STATUS_COLORS = {
	[ORDER_STATUS.PLACED]: 'bg-blue-500',
	[ORDER_STATUS.CONFIRMED]: 'bg-blue-600',
	[ORDER_STATUS.PREPARING]: 'bg-orange-500',
	[ORDER_STATUS.READY]: 'bg-green-500',
	[ORDER_STATUS.PICKED_UP]: 'bg-teal-500',
	[ORDER_STATUS.ON_THE_WAY]: 'bg-purple-500',
	[ORDER_STATUS.DELIVERED]: 'bg-green-600',
	[ORDER_STATUS.CANCELLED]: 'bg-red-500',
	[ORDER_STATUS.REJECTED]: 'bg-red-700',
	[ORDER_STATUS.DELAYED]: 'bg-yellow-500',
}

// Status Labels (user-friendly)
export const STATUS_LABELS = {
	[ORDER_STATUS.PLACED]: 'Order Placed',
	[ORDER_STATUS.CONFIRMED]: 'Confirmed',
	[ORDER_STATUS.PREPARING]: 'Preparing',
	[ORDER_STATUS.READY]: 'Ready',
	[ORDER_STATUS.PICKED_UP]: 'Picked Up',
	[ORDER_STATUS.ON_THE_WAY]: 'On The Way',
	[ORDER_STATUS.DELIVERED]: 'Delivered',
	[ORDER_STATUS.CANCELLED]: 'Cancelled',
	[ORDER_STATUS.REJECTED]: 'Rejected',
	[ORDER_STATUS.DELAYED]: 'Delayed',
}

// Runner Statuses
export const RUNNER_STATUS = {
	AVAILABLE: 'Available',
	BUSY: 'Busy',
	OFFLINE: 'Offline',
}

// Priority Types
export const PRIORITY = {
	REGULAR: 'Regular',
	URGENT: 'Urgent',
}
