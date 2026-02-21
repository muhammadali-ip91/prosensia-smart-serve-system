# ProSensia Feature Matrix (API vs UI)

This matrix maps backend endpoints to roles and current UI visibility.

Legend for **Missing in UI**:
- **No** = visible/usable from UI
- **Yes** = backend-only (no direct UI control/screen)

| Endpoint | Role | UI me kaha show hota hai | Missing in UI (yes/no) |
|---|---|---|---|
| `POST /auth/login` | Public | Login page (`/login`) | No |
| `POST /auth/refresh` | Authenticated | Silent token refresh in Axios interceptor (no button) | Yes |
| `GET /auth/me` | Authenticated | Session restore on app load | No |
| `POST /auth/logout` | Authenticated | Navbar logout (server-side + local cleanup) | No |
| `POST /orders` | Engineer | Cart checkout (`/cart`) | No |
| `GET /orders` | Engineer | My Orders (`/orders`) | No |
| `GET /orders/{order_id}` | Authenticated (access rules apply) | Order Tracking (`/order/track/:orderId`) | No |
| `DELETE /orders/{order_id}` | Owner/Admin | Cancel from Order Tracking page | No |
| `POST /orders/{order_id}/feedback` | Engineer | Feedback page (`/feedback/:orderId`) | No |
| `GET /menu` | Authenticated | Engineer Menu (`/menu`) | No |
| `GET /menu/all` | Authenticated | Admin Menu Management + Kitchen availability panel | No |
| `GET /kitchen/orders` | Kitchen | Kitchen Dashboard (`/kitchen`) | No |
| `PATCH /kitchen/orders/{order_id}/status` | Kitchen | Kitchen Dashboard status buttons | No |
| `PATCH /kitchen/menu/{item_id}/availability` | Kitchen | Kitchen Dashboard “Manage Menu Availability” | No |
| `GET /kitchen/settings` | Kitchen | Kitchen Dashboard “Kitchen Open/Close Control” | No |
| `PATCH /kitchen/settings/hours` | Kitchen | Kitchen Dashboard “Save Hours” | No |
| `PATCH /kitchen/settings/toggle` | Kitchen | Kitchen Dashboard “Open Now / Close Now” | No |
| `GET /runner/deliveries` | Runner | Runner Dashboard (`/runner`) | No |
| `PATCH /runner/deliveries/{order_id}/status` | Runner | Runner delivery action buttons | No |
| `PATCH /runner/status` | Runner | Runner availability toggle | No |
| `GET /admin/dashboard` | Admin | Admin Dashboard (`/admin`) | No |
| `GET /admin/popular-items` | Admin | Not wired in current UI | Yes |
| `POST /admin/menu` | Admin | Admin Menu Management add modal | No |
| `POST /admin/menu/upload-image` | Admin | Admin Menu add/edit image upload | No |
| `PUT /admin/menu/{item_id}` | Admin | Admin Menu edit modal | No |
| `DELETE /admin/menu/{item_id}` | Admin | Admin Menu table delete action | No |
| `GET /admin/users` | Admin | Admin User Management page | No |
| `POST /admin/users` | Admin | Admin User Management “Add User” modal | No |
| `PUT /admin/users/{user_id}/toggle` | Admin | Admin User Management active/deactive action | No |
| `GET /notifications` | Authenticated | Notification bell dropdown/context | No |
| `PATCH /notifications/read` | Authenticated | Notification read state updates | No |
| `GET /trivia/question` | Engineer | Trivia game page (`/trivia`) | No |
| `POST /trivia/answer` | Engineer | Trivia game submit answer | No |
| `GET /trivia/leaderboard` | Engineer | Trivia leaderboard page (`/trivia/leaderboard`) | No |
| `GET /health` | Public/Monitoring | Admin Dashboard "System Health" panel | No |
| `GET /` | Public | No dedicated UI page | Yes |

## Quick Summary

- **UI-wired endpoints:** 31
- **Backend-only / hidden endpoints:** 3
  - `POST /auth/refresh` (background/internal)
  - `GET /admin/popular-items`
  - `GET /`

## Suggested Next UI Improvements

1. Add a small “Popular Items” card/widget in Admin Dashboard.
2. Optional dedicated System page (history + alerts), beyond current health snapshot.

## Role-wise Matrix

### Engineer

| Endpoint | UI me kaha show hota hai | Missing in UI (yes/no) |
|---|---|---|
| `POST /orders` | Cart checkout (`/cart`) | No |
| `GET /orders` | My Orders (`/orders`) | No |
| `GET /orders/{order_id}` | Order Tracking (`/order/track/:orderId`) | No |
| `DELETE /orders/{order_id}` | Cancel from Order Tracking page | No |
| `POST /orders/{order_id}/feedback` | Feedback page (`/feedback/:orderId`) | No |
| `GET /menu` | Engineer Menu (`/menu`) | No |
| `GET /trivia/question` | Trivia game page (`/trivia`) | No |
| `POST /trivia/answer` | Trivia game submit | No |
| `GET /trivia/leaderboard` | Leaderboard page (`/trivia/leaderboard`) | No |
| `GET /notifications` | Notification bell dropdown | No |
| `PATCH /notifications/read` | Notification read actions | No |

### Kitchen

| Endpoint | UI me kaha show hota hai | Missing in UI (yes/no) |
|---|---|---|
| `GET /kitchen/orders` | Kitchen Dashboard (`/kitchen`) | No |
| `PATCH /kitchen/orders/{order_id}/status` | Incoming/Preparing action buttons | No |
| `PATCH /kitchen/menu/{item_id}/availability` | Manage Menu Availability section | No |
| `GET /kitchen/settings` | Kitchen Open/Close Control card | No |
| `PATCH /kitchen/settings/hours` | Save Hours button | No |
| `PATCH /kitchen/settings/toggle` | Open Now / Close Now | No |
| `GET /menu/all` | Menu list inside Kitchen dashboard | No |

### Runner

| Endpoint | UI me kaha show hota hai | Missing in UI (yes/no) |
|---|---|---|
| `GET /runner/deliveries` | Runner Dashboard (`/runner`) | No |
| `PATCH /runner/deliveries/{order_id}/status` | Delivery status action buttons | No |
| `PATCH /runner/status` | Runner availability toggle | No |

### Admin

| Endpoint | UI me kaha show hota hai | Missing in UI (yes/no) |
|---|---|---|
| `GET /admin/dashboard` | Admin Dashboard (`/admin`) | No |
| `GET /admin/popular-items` | Not wired in current UI | Yes |
| `POST /admin/menu` | Menu Management add modal | No |
| `POST /admin/menu/upload-image` | Menu add/edit image upload | No |
| `PUT /admin/menu/{item_id}` | Menu edit modal | No |
| `DELETE /admin/menu/{item_id}` | Menu table delete action | No |
| `GET /admin/users` | User Management list | No |
| `POST /admin/users` | User Management add modal | No |
| `PUT /admin/users/{user_id}/toggle` | User active/deactive action | No |

### Common / Platform

| Endpoint | UI me kaha show hota hai | Missing in UI (yes/no) |
|---|---|---|
| `POST /auth/login` | Login page | No |
| `GET /auth/me` | App session restore | No |
| `POST /auth/refresh` | Background token refresh | Yes |
| `POST /auth/logout` | Navbar logout action | No |
| `GET /health` | Admin Dashboard health panel | No |
| `GET /` | No dedicated page | Yes |
