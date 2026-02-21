# ❌ ProSensia Smart-Serve — Error Codes Reference

---

## Error Response Format

```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable description",
        "details": {}
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "REQ-abc123"
}
Authentication Errors (AUTH_xxx)
Code	HTTP	Message	Resolution
AUTH_001	401	Invalid credentials	Check employee ID & password
AUTH_002	401	Token expired	Use refresh token
AUTH_003	403	Insufficient permissions	Check user role
AUTH_004	403	Account deactivated	Contact admin
AUTH_005	401	Invalid token	Re-login
AUTH_006	429	Too many login attempts	Wait 15 minutes
Order Errors (ORD_xxx)
Code	HTTP	Message	Resolution
ORD_001	400	Invalid order data	Check request body
ORD_002	400	Item unavailable	Remove item from order
ORD_003	400	Cannot modify order in current status	Order already being prepared
ORD_004	400	Cannot cancel order in current status	Order already being prepared
ORD_005	409	Duplicate order detected	Wait 30 seconds
ORD_006	400	Kitchen is closed	Order during working hours
ORD_007	404	Order not found	Check order ID
ORD_008	400	Empty order	Add at least one item
Runner Errors (RUN_xxx)
Code	HTTP	Message	Resolution
RUN_001	503	No runners available	Order queued automatically
RUN_002	400	Runner at max capacity	Wait for runner to free up
RUN_003	400	Runner went offline	Order reassigned
RUN_004	400	Invalid status transition	Check allowed transitions
System Errors (SYS_xxx)
Code	HTTP	Message	Resolution
SYS_001	503	Database connection error	Retry after a moment
SYS_002	500	AI model unavailable	Fallback ETA used
SYS_003	503	Service overloaded	Retry after a moment
SYS_004	500	Internal server error	Contact support
SYS_005	400	Invalid QR code	Scan a valid QR code
SYS_006	400	QR token expired	Contact admin for new QR
Validation Errors (VAL_xxx)
Code	HTTP	Message	Resolution
VAL_001	422	Missing required field	Check API documentation
VAL_002	422	Invalid field value	Check allowed values
VAL_003	422	Value out of range	Check min/max limits
Rate Limit Errors
Code	HTTP	Message
RATE_LIMITED	429	Too many requests. Try again in X seconds
text
