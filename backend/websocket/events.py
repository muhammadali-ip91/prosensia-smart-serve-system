"""WebSocket Event Definitions"""

# Event names used across the system

class SocketEvents:
    # Server -> Client
    ORDER_STATUS_UPDATE = "order_status_update"
    NEW_ORDER = "new_order"
    NEW_DELIVERY = "new_delivery"
    ETA_UPDATE = "eta_update"
    NOTIFICATION = "notification"
    ORDER_CANCELLED = "order_cancelled"
    DELIVERY_REASSIGNED = "delivery_reassigned"

    # Client -> Server
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
