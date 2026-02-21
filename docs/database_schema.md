# 🗄️ ProSensia Smart-Serve — Database Schema

## Database: PostgreSQL 15
## Tables: 13

---

## Entity Relationship Diagram
users ──────────┬──── orders ──── order_items ──── menu_items
│ │
│ ├──── runners
│ │
│ ├──── order_status_history
│ │
│ ├──── feedback
│ │
│ └──── ai_training_data
│
├──── notifications
│
└──── trivia_scores ──── trivia_questions

stations (linked to orders)
system_logs (standalone)

text


---

## Table Descriptions

### 1. users
All system users (engineers, kitchen staff, runners, admins).

| Column        | Type         | Constraints              |
|---------------|--------------|--------------------------|
| user_id       | VARCHAR(20)  | PRIMARY KEY              |
| name          | VARCHAR(100) | NOT NULL                 |
| email         | VARCHAR(100) | UNIQUE, NOT NULL         |
| password_hash | VARCHAR(255) | NOT NULL                 |
| role          | VARCHAR(20)  | NOT NULL                 |
| department    | VARCHAR(50)  |                          |
| phone         | VARCHAR(15)  |                          |
| is_active     | BOOLEAN      | DEFAULT TRUE             |
| created_at    | TIMESTAMP    | DEFAULT NOW()            |
| updated_at    | TIMESTAMP    | DEFAULT NOW()            |

**Indexes:** email, role

---

### 2. stations
Factory workstations where engineers work.

| Column                | Type         | Constraints    |
|-----------------------|--------------|----------------|
| station_id            | VARCHAR(20)  | PRIMARY KEY    |
| station_name          | VARCHAR(50)  | NOT NULL       |
| floor                 | INTEGER      | NOT NULL       |
| building              | VARCHAR(50)  | NOT NULL       |
| distance_from_kitchen | INTEGER      | NOT NULL       |
| qr_token              | VARCHAR(255) | NOT NULL       |
| qr_token_expires_at   | TIMESTAMP    | NOT NULL       |
| is_active             | BOOLEAN      | DEFAULT TRUE   |

---

### 3. menu_items
Food items available for ordering.

| Column             | Type          | Constraints    |
|--------------------|---------------|----------------|
| item_id            | SERIAL        | PRIMARY KEY    |
| item_name          | VARCHAR(100)  | NOT NULL       |
| category           | VARCHAR(50)   | NOT NULL       |
| price              | DECIMAL(10,2) | NOT NULL       |
| prep_time_estimate | INTEGER       | NOT NULL       |
| complexity_score   | INTEGER       | DEFAULT 1      |
| image_url          | VARCHAR(500)  |                |
| is_available       | BOOLEAN       | DEFAULT TRUE   |
| unavailable_reason | VARCHAR(200)  |                |
| created_at         | TIMESTAMP     | DEFAULT NOW()  |
| updated_at         | TIMESTAMP     | DEFAULT NOW()  |

**Indexes:** category, is_available

---

### 4. orders
All orders placed in the system.

| Column               | Type          | Constraints         |
|----------------------|---------------|---------------------|
| order_id             | VARCHAR(20)   | PRIMARY KEY         |
| engineer_id          | VARCHAR(20)   | FK → users          |
| station_id           | VARCHAR(20)   | FK → stations       |
| priority             | VARCHAR(10)   | DEFAULT 'Regular'   |
| status               | VARCHAR(20)   | DEFAULT 'Placed'    |
| runner_id            | VARCHAR(20)   | FK → users          |
| special_instructions | VARCHAR(500)  |                     |
| total_price          | DECIMAL(10,2) |                     |
| ai_predicted_eta     | INTEGER       |                     |
| actual_delivery_time | INTEGER       |                     |
| cancelled_reason     | VARCHAR(200)  |                     |
| created_at           | TIMESTAMP     | DEFAULT NOW()       |
| updated_at           | TIMESTAMP     | DEFAULT NOW()       |
| delivered_at         | TIMESTAMP     |                     |

**Indexes:** engineer_id, runner_id, status, created_at

---

### 5. order_items
Individual items within each order.

| Column        | Type          | Constraints       |
|---------------|---------------|-----------------  |
| order_item_id | SERIAL        | PRIMARY KEY       |
| order_id      | VARCHAR(20)   | FK → orders       |
| item_id       | INTEGER       | FK → menu_items   |
| quantity      | INTEGER       | DEFAULT 1         |
| item_price    | DECIMAL(10,2) | NOT NULL          |
| subtotal      | DECIMAL(10,2) | NOT NULL          |

---

### 6. runners
Extended information for delivery runners.

| Column                | Type          | Constraints       |
|-----------------------|---------------|-------------------|
| runner_id             | VARCHAR(20)   | PK, FK → users    |
| current_status        | VARCHAR(20)   | DEFAULT Available  |
| active_order_count    | INTEGER       | DEFAULT 0         |
| max_capacity          | INTEGER       | DEFAULT 5         |
| current_location      | VARCHAR(50)   |                   |
| total_deliveries      | INTEGER       | DEFAULT 0         |
| average_delivery_time | DECIMAL(5,2)  | DEFAULT 0         |

---

### 7. order_status_history
Audit trail for all status changes.

| Column     | Type        | Constraints       |
|------------|-------------|-------------------|
| history_id | SERIAL      | PRIMARY KEY       |
| order_id   | VARCHAR(20) | FK → orders       |
| old_status | VARCHAR(20) |                   |
| new_status | VARCHAR(20) | NOT NULL          |
| changed_by | VARCHAR(20) | FK → users        |
| changed_at | TIMESTAMP   | DEFAULT NOW()     |
| notes      | VARCHAR(200)|                   |

---

### 8. feedback
Engineer feedback after delivery.

| Column      | Type        | Constraints          |
|-------------|-------------|----------------------|
| feedback_id | SERIAL      | PRIMARY KEY          |
| order_id    | VARCHAR(20) | UNIQUE, FK → orders  |
| engineer_id | VARCHAR(20) | FK → users           |
| rating      | INTEGER     | CHECK 1-5            |
| comment     | VARCHAR(500)|                      |
| created_at  | TIMESTAMP   | DEFAULT NOW()        |

---

### 9. notifications
All system notifications.

| Column          | Type        | Constraints       |
|-----------------|-------------|-------------------|
| notification_id | SERIAL      | PRIMARY KEY       |
| user_id         | VARCHAR(20) | FK → users        |
| type            | VARCHAR(50) | NOT NULL          |
| title           | VARCHAR(200)| NOT NULL          |
| message         | VARCHAR(500)| NOT NULL          |
| priority        | VARCHAR(10) | DEFAULT normal    |
| is_read         | BOOLEAN     | DEFAULT FALSE     |
| action_url      | VARCHAR(200)|                   |
| created_at      | TIMESTAMP   | DEFAULT NOW()     |

---

### 10. trivia_questions
Quiz questions for engagement module.

| Column         | Type        | Constraints       |
|----------------|-------------|-------------------|
| question_id    | SERIAL      | PRIMARY KEY       |
| question_text  | VARCHAR(500)| NOT NULL          |
| option_a       | VARCHAR(200)| NOT NULL          |
| option_b       | VARCHAR(200)| NOT NULL          |
| option_c       | VARCHAR(200)| NOT NULL          |
| option_d       | VARCHAR(200)| NOT NULL          |
| correct_option | CHAR(1)     | NOT NULL          |
| category       | VARCHAR(50) |                   |
| difficulty     | VARCHAR(10) |                   |
| is_active      | BOOLEAN     | DEFAULT TRUE      |

---

### 11. trivia_scores
Engineer trivia scores.

| Column             | Type        | Constraints              |
|--------------------|-------------|--------------------------|
| score_id           | SERIAL      | PRIMARY KEY              |
| engineer_id        | VARCHAR(20) | FK → users               |
| question_id        | INTEGER     | FK → trivia_questions    |
| answered_correctly | BOOLEAN     | NOT NULL                 |
| time_taken_seconds | INTEGER     |                          |
| points_earned      | INTEGER     | DEFAULT 0                |
| played_at          | TIMESTAMP   | DEFAULT NOW()            |

---

### 12. ai_training_data
Data collected for AI model training.

| Column                  | Type          | Constraints   |
|-------------------------|---------------|---------------|
| record_id               | SERIAL        | PRIMARY KEY   |
| order_id                | VARCHAR(20)   | FK → orders   |
| hour_of_day             | INTEGER       |               |
| day_of_week             | INTEGER       |               |
| active_orders_at_time   | INTEGER       |               |
| item_complexity         | INTEGER       |               |
| total_items             | INTEGER       |               |
| available_runners       | INTEGER       |               |
| kitchen_queue_length    | INTEGER       |               |
| avg_prep_time           | DECIMAL(5,2)  |               |
| station_distance        | INTEGER       |               |
| is_peak_hour            | BOOLEAN       |               |
| priority_encoded        | INTEGER       |               |
| predicted_eta           | INTEGER       |               |
| actual_delivery_minutes | INTEGER       |               |
| prediction_error        | INTEGER       |               |
| recorded_at             | TIMESTAMP     | DEFAULT NOW() |

---

### 13. system_logs
Application logs stored in database.

| Column           | Type          | Constraints   |
|------------------|---------------|---------------|
| log_id           | SERIAL        | PRIMARY KEY   |
| log_level        | VARCHAR(10)   | NOT NULL      |
| module           | VARCHAR(50)   | NOT NULL      |
| message          | VARCHAR(1000) | NOT NULL      |
| user_id          | VARCHAR(20)   |               |
| request_path     | VARCHAR(200)  |               |
| response_code    | INTEGER       |               |
| response_time_ms | INTEGER       |               |
| created_at       | TIMESTAMP     | DEFAULT NOW() |
