# 📡 ProSensia Smart-Serve — API Documentation

## Base URL: `http://localhost:8000`

## Interactive Docs: `http://localhost:8000/docs`

---

## Authentication

All API requests (except `/auth/login`, `/health`) require a JWT token
in the Authorization header:
Authorization: Bearer <your_jwt_token>

text


---

## 1. Authentication Endpoints

### POST /auth/login
Login and receive JWT tokens.

**Request:**
```json
{
    "employee_id": "ENG-001",
    "password": "test123"
}
Response (200):

JSON

{
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "role": "engineer",
    "user_info": {
        "user_id": "ENG-001",
        "name": "Aarav Sharma",
        "email": "aarav.sharma1@prosensia.com",
        "role": "engineer",
        "department": "Assembly Line"
    }
}
Error (401):

JSON

{
    "success": false,
    "error": {
        "code": "AUTH_001",
        "message": "Invalid credentials"
    }
}
POST /auth/refresh
Refresh an expired access token.

Request:

JSON

{
    "refresh_token": "eyJhbGciOi..."
}
Response (200):

JSON

{
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer"
}
POST /auth/logout
Invalidate current tokens.

Headers: Authorization: Bearer <token>

Response (200):

JSON

{
    "message": "Logged out successfully"
}
GET /auth/me
Get current user information.

Headers: Authorization: Bearer <token>

Response (200):

JSON

{
    "user_id": "ENG-001",
    "name": "Aarav Sharma",
    "role": "engineer",
    "department": "Assembly Line",
    "station": "Bay-12"
}
2. Menu Endpoints
GET /menu
Get available menu items.

Headers: Authorization: Bearer <token>

Response (200):

JSON

{
    "categories": [
        {
            "name": "Snacks",
            "items": [
                {
                    "id": 1,
                    "name": "Samosa",
                    "price": 20,
                    "prep_time": 5,
                    "complexity_score": 1,
                    "available": true,
                    "image_url": "/images/menu/samosa.jpg"
                },
                {
                    "id": 2,
                    "name": "Vada Pav",
                    "price": 25,
                    "prep_time": 5,
                    "complexity_score": 1,
                    "available": false,
                    "unavailable_reason": "Out of stock"
                }
            ]
        },
        {
            "name": "Main Course",
            "items": [...]
        },
        {
            "name": "Beverages",
            "items": [...]
        }
    ]
}
3. Order Endpoints
POST /orders
Place a new order.

Auth: Engineer role required

Request:

JSON

{
    "station_id": "Bay-12",
    "items": [
        { "item_id": 1, "quantity": 2 },
        { "item_id": 5, "quantity": 1 }
    ],
    "priority": "Regular",
    "special_instructions": "Less spicy"
}
Response (201):

JSON

{
    "order_id": "ORD-2024-0001",
    "estimated_wait_time": 12,
    "ai_eta_source": "ai_model",
    "ai_confidence": 0.85,
    "assigned_runner": "RUN-003",
    "status": "Placed",
    "total_price": 100,
    "items": [...],
    "factors": {
        "kitchen_load": "Medium",
        "runner_availability": "High",
        "peak_hour": "No",
        "item_complexity": "Low"
    },
    "created_at": "2024-01-15T10:30:00Z"
}
GET /orders/{order_id}
Get order details.

Auth: Order owner, assigned runner, kitchen, or admin

Response (200):

JSON

{
    "order_id": "ORD-2024-0001",
    "station_id": "Bay-12",
    "engineer_id": "ENG-001",
    "items": [
        {
            "item_id": 1,
            "item_name": "Samosa",
            "quantity": 2,
            "price": 20,
            "subtotal": 40
        }
    ],
    "priority": "Regular",
    "status": "Preparing",
    "assigned_runner": "RUN-003",
    "ai_predicted_eta": 12,
    "total_price": 100,
    "special_instructions": "Less spicy",
    "status_history": [
        { "status": "Placed", "timestamp": "2024-01-15T10:30:00Z" },
        { "status": "Confirmed", "timestamp": "2024-01-15T10:30:05Z" },
        { "status": "Preparing", "timestamp": "2024-01-15T10:31:00Z" }
    ],
    "created_at": "2024-01-15T10:30:00Z"
}
PATCH /orders/{order_id}
Modify order (only if status is "Placed").

Auth: Order owner only

Request:

JSON

{
    "items": [
        { "item_id": 1, "quantity": 3 },
        { "item_id": 7, "quantity": 1 }
    ],
    "special_instructions": "Extra sauce"
}
Response (200):

JSON

{
    "message": "Order updated successfully",
    "order_id": "ORD-2024-0001",
    "new_total": 95,
    "updated_eta": 14
}
DELETE /orders/{order_id}
Cancel order (only if "Placed" or "Confirmed").

Auth: Order owner or admin

Response (200):

JSON

{
    "message": "Order cancelled successfully",
    "order_id": "ORD-2024-0001"
}
Error (400):

JSON

{
    "success": false,
    "error": {
        "code": "ORD_004",
        "message": "Cannot cancel order in 'Preparing' status"
    }
}
GET /orders/my-orders
Get order history for logged-in engineer.

Auth: Engineer role required

Query Parameters:

page (default: 1)
per_page (default: 10)
status (optional filter)
Response (200):

JSON

{
    "orders": [...],
    "total_count": 25,
    "page": 1,
    "per_page": 10,
    "total_pages": 3
}
POST /orders/{order_id}/feedback
Submit feedback after delivery.

Auth: Order owner only

Request:

JSON

{
    "rating": 4,
    "comment": "Food was great, slightly delayed"
}
Response (201):

JSON

{
    "feedback_id": 1,
    "message": "Feedback submitted successfully"
}
4. Kitchen Endpoints
GET /kitchen/orders
Get all active orders for kitchen.

Auth: Kitchen role required

Response (200):

JSON

{
    "orders": [
        {
            "order_id": "ORD-2024-0001",
            "station_id": "Bay-12",
            "priority": "Urgent",
            "status": "Placed",
            "items": [...],
            "special_instructions": "Less spicy",
            "created_at": "2024-01-15T10:30:00Z",
            "elapsed_minutes": 3
        }
    ]
}
PATCH /kitchen/orders/{order_id}/status
Update preparation status.

Auth: Kitchen role required

Request:

JSON

{
    "status": "Preparing"
}
Allowed transitions: Placed/Confirmed → Preparing → Ready

PATCH /kitchen/menu/{item_id}/availability
Toggle menu item availability.

Auth: Kitchen role required

Request:

JSON

{
    "available": false,
    "reason": "Out of stock"
}
5. Runner Endpoints
GET /runner/deliveries
Get assigned deliveries.

Auth: Runner role required

PATCH /runner/deliveries/{order_id}/status
Update delivery status.

Auth: Assigned runner only

Request:

JSON

{
    "status": "Delivered"
}
Allowed transitions: Ready → PickedUp → OnTheWay → Delivered

PATCH /runner/status
Update runner availability.

Auth: Runner role required

Request:

JSON

{
    "status": "Available"
}
Allowed values: Available, Busy, Offline

6. Admin Endpoints
GET /admin/dashboard
System overview statistics.

Auth: Admin role required

POST /admin/menu
Add new menu item.

PUT /admin/menu/{item_id}
Update menu item.

DELETE /admin/menu/{item_id}
Delete menu item.

GET /admin/users
List all users.

POST /admin/users
Create new user.

PUT /admin/users/{user_id}
Update user.

GET /admin/reports?type=daily&date=2024-01-15
Get analytics reports.

7. Notification Endpoints
GET /notifications
Get notifications for current user.

Auth: Any authenticated user

PATCH /notifications/{id}/read
Mark notification as read.

8. Trivia Endpoints
GET /trivia/question
Get a random trivia question.

Auth: Engineer role required

POST /trivia/answer
Submit trivia answer.

Request:

JSON

{
    "question_id": 1,
    "selected_option": "B",
    "time_taken_seconds": 8
}
GET /trivia/leaderboard
Get weekly leaderboard.

9. System Endpoints
GET /health
System health check (no auth required).

Response (200):

JSON

{
    "status": "healthy",
    "database": "connected",
    "redis": "connected",
    "ai_model": "loaded",
    "uptime": "48h 23m",
    "active_connections": 45,
    "timestamp": "2024-01-15T10:30:00Z"
}
Error Response Format
All errors follow this structure:

JSON

{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {}
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "REQ-abc123"
}
Rate Limits
Endpoint	Limit
/auth/login	10 requests / 15 minutes
All other	100 requests / minute
Rate limit exceeded response (429):

JSON

{
    "success": false,
    "error": {
        "code": "RATE_LIMITED",
        "message": "Too many requests. Try again in 30 seconds."
    }
}
text
