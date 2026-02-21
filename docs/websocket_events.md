Server → Client Events
1. order_status_update
Sent to engineer when their order status changes.

Room: engineer_{engineer_id}

JSON

{
    "event": "order_status_update",
    "data": {
        "order_id": "ORD-2024-0001",
        "old_status": "Confirmed",
        "new_status": "Preparing",
        "updated_eta": 10,
        "runner_name": "Raju Kumar",
        "timestamp": "2024-01-15T10:35:00Z"
    }
}
2. eta_update
Sent when ETA changes dynamically.

Room: engineer_{engineer_id}

JSON

{
    "event": "eta_update",
    "data": {
        "order_id": "ORD-2024-0001",
        "new_eta": 15,
        "previous_eta": 12,
        "reason": "Kitchen load increased",
        "confidence": 0.78
    }
}
3. new_order
Sent to kitchen when a new order arrives.

Room: kitchen

JSON

{
    "event": "new_order",
    "data": {
        "order_id": "ORD-2024-0001",
        "station": "Bay-12",
        "items": [
            { "name": "Biryani", "quantity": 1 },
            { "name": "Chai", "quantity": 2 }
        ],
        "priority": "Urgent",
        "special_instructions": "Less spicy",
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
4. order_cancelled
Sent to kitchen when engineer cancels order.

Room: kitchen

JSON

{
    "event": "order_cancelled",
    "data": {
        "order_id": "ORD-2024-0001",
        "cancelled_by": "ENG-001",
        "reason": "Changed mind"
    }
}
5. new_delivery
Sent to runner when a delivery is assigned.

Room: runner_{runner_id}

JSON

{
    "event": "new_delivery",
    "data": {
        "order_id": "ORD-2024-0001",
        "pickup_location": "Kitchen Counter",
        "delivery_station": "Bay-12",
        "building": "Building-A",
        "floor": 2,
        "items": [...],
        "priority": "Urgent"
    }
}
6. delivery_reassigned
Sent when a delivery is reassigned to different runner.

Room: runner_{runner_id}

JSON

{
    "event": "delivery_reassigned",
    "data": {
        "order_id": "ORD-2024-0001",
        "reason": "Previous runner went offline",
        "reassigned_at": "2024-01-15T10:40:00Z"
    }
}
7. notification
Generic notification event.

Room: {role}_{user_id} or shared room

JSON

{
    "event": "notification",
    "data": {
        "notification_id": "NOTIF-001",
        "type": "order_ready",
        "title": "Order Ready!",
        "message": "Your order is ready for pickup.",
        "priority": "high",
        "action_url": "/orders/ORD-2024-0001/track"
    }
}
8. system_alert
Sent to admins for system events.

Room: admin

JSON

{
    "event": "system_alert",
    "data": {
        "type": "runner_shortage",
        "message": "All runners are busy. 3 orders queued.",
        "severity": "warning",
        "timestamp": "2024-01-15T13:00:00Z"
    }
}
Client → Server Events
1. join_room
Join a specific room after authentication.

JavaScript

socket.emit("join_room", {
    room: "engineer_ENG-001"
});
2. leave_room
Leave a room.

JavaScript

socket.emit("leave_room", {
    room: "engineer_ENG-001"
});
3. ping
Keep-alive heartbeat.

JavaScript

socket.emit("ping");
// Server responds with "pong"
Reconnection Strategy
text

Attempt 1: Wait 1 second
Attempt 2: Wait 2 seconds
Attempt 3: Wait 4 seconds
Attempt 4: Wait 8 seconds
Attempt 5: Wait 16 seconds
Attempt 6-10: Wait 30 seconds (max)

After 10 failed attempts:
  → Show "Connection lost" banner
  → Offer manual reconnect button
  → Fall back to polling (GET /orders/{id} every 10s)
text
