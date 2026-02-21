# 🤖 ProSensia Smart-Serve — AI Model Guide

---

## Overview

The AI module predicts Estimated Time of Arrival (ETA) for food orders
using a Random Forest Regressor trained on historical order data.

---

## Architecture
Order Placed
│
▼
Feature Engineering ──→ 11 Features Extracted
│
▼
Model Prediction ──→ ETA in minutes + Confidence Score
│
├── Success → Return AI prediction
│
└── Failure → Return Fallback prediction (rule-based)

text


---

## Features Used (11 total)

| #  | Feature                | Description                          |
|----|------------------------|--------------------------------------|
| 1  | hour_of_day            | Hour when order placed (0-23)        |
| 2  | day_of_week            | Day of week (0=Mon, 6=Sun)           |
| 3  | active_orders_count    | Currently active orders              |
| 4  | item_complexity        | Weighted complexity score            |
| 5  | total_items            | Number of items in order             |
| 6  | available_runners      | Available runners count              |
| 7  | kitchen_queue_length   | Orders ahead in queue                |
| 8  | avg_prep_time          | Average prep time of items           |
| 9  | station_distance       | Distance from kitchen (meters)       |
| 10 | is_peak_hour           | Whether peak hour (0 or 1)           |
| 11 | priority_encoded       | Regular=0, Urgent=1                  |

---

## Quick Start

```bash
# Step 1: Generate training data
python -m ai_module.scripts.generate_data

# Step 2: Train model
python -m ai_module.scripts.train_model

# Step 3: Evaluate model
python -m ai_module.scripts.evaluate_model

# Step 4: Retrain with real data (weekly)
python -m ai_module.scripts.retrain
Model Details
Algorithm: Random Forest Regressor
Library: Scikit-Learn
Training Data: 4000 records (80% of 5000 generated)
Test Data: 1000 records (20%)
Target: MAE < 3.0 minutes
Accuracy Threshold: Model saved only if MAE < 3.0
Fallback Mechanism
If AI model is unavailable, the system uses rule-based prediction:

text

ETA = prep_time + queue_wait + delivery_time + runner_penalty
    × peak_hour_multiplier
    × urgent_discount
The engineer NEVER sees a blank ETA.

Retraining
Frequency: Weekly (automated via GitHub Actions)
Data Source: ai_training_data table in PostgreSQL
Comparison: New model only replaces old if it's better
Backup: Previous model is always backed up
text
