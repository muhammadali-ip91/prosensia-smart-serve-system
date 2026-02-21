"""
Seed Data - Initial data for the system
Run this to populate database with initial data
"""

from database.connection import SessionLocal
from models.user_model import User
from models.station_model import Station
from models.menu_item_model import MenuItem
from models.runner_model import Runner
from models.trivia_question_model import TriviaQuestion
from auth.password_handler import hash_password
from loguru import logger
from datetime import datetime, timedelta


def seed_all():
	"""Run all seed functions"""
	db = SessionLocal()
	try:
		seed_users(db)
		db.flush()
		seed_stations(db)
		db.flush()
		seed_menu_items(db)
		db.flush()
		seed_runners(db)
		db.flush()
		seed_trivia_questions(db)
		db.flush()
		db.commit()
		logger.info("✅ All seed data inserted successfully!")
	except Exception as e:
		db.rollback()
		logger.error(f"❌ Seed data error: {e}")
		raise
	finally:
		db.close()


def seed_users(db):
	"""Create default users for each role"""

	users = [
		# Admin
		{
			"user_id": "ADM-001",
			"name": "Admin User",
			"email": "admin@prosensia.com",
			"password_hash": hash_password("admin123"),
			"role": "admin",
			"department": "Management",
			"phone": "03001234567",
			"is_active": True
		},
		# Kitchen Staff
		{
			"user_id": "KIT-001",
			"name": "Chef Ahmed",
			"email": "kitchen1@prosensia.com",
			"password_hash": hash_password("kitchen123"),
			"role": "kitchen",
			"department": "Kitchen",
			"phone": "03011234567",
			"is_active": True
		},
		{
			"user_id": "KIT-002",
			"name": "Chef Sara",
			"email": "kitchen2@prosensia.com",
			"password_hash": hash_password("kitchen123"),
			"role": "kitchen",
			"department": "Kitchen",
			"phone": "03021234567",
			"is_active": True
		},
		# Runners
		{
			"user_id": "RUN-001",
			"name": "Runner Ali",
			"email": "runner1@prosensia.com",
			"password_hash": hash_password("runner123"),
			"role": "runner",
			"department": "Delivery",
			"phone": "03031234567",
			"is_active": True
		},
		{
			"user_id": "RUN-002",
			"name": "Runner Bilal",
			"email": "runner2@prosensia.com",
			"password_hash": hash_password("runner123"),
			"role": "runner",
			"department": "Delivery",
			"phone": "03041234567",
			"is_active": True
		},
		{
			"user_id": "RUN-003",
			"name": "Runner Kashif",
			"email": "runner3@prosensia.com",
			"password_hash": hash_password("runner123"),
			"role": "runner",
			"department": "Delivery",
			"phone": "03051234567",
			"is_active": True
		},
		{
			"user_id": "RUN-004",
			"name": "Runner Daniyal",
			"email": "runner4@prosensia.com",
			"password_hash": hash_password("runner123"),
			"role": "runner",
			"department": "Delivery",
			"phone": "03061234567",
			"is_active": True
		},
		{
			"user_id": "RUN-005",
			"name": "Runner Ehsan",
			"email": "runner5@prosensia.com",
			"password_hash": hash_password("runner123"),
			"role": "runner",
			"department": "Delivery",
			"phone": "03071234567",
			"is_active": True
		},
	]

	# Add 10 Engineers
	for i in range(1, 11):
		users.append({
			"user_id": f"ENG-{i:03d}",
			"name": f"Engineer {i}",
			"email": f"engineer{i}@prosensia.com",
			"password_hash": hash_password("engineer123"),
			"role": "engineer",
			"department": "Production",
			"phone": f"030{i}1234567",
			"is_active": True
		})

	for user_data in users:
		existing = db.query(User).filter(User.user_id == user_data["user_id"]).first()
		if not existing:
			user = User(**user_data)
			db.add(user)

	logger.info(f"✅ {len(users)} users seeded")


def seed_stations(db):
	"""Create workstation data"""

	stations = []
	buildings = ["Building-A", "Building-B"]
	floors = [1, 2, 3]

	station_num = 1
	for building in buildings:
		for floor in floors:
			for bay in range(1, 9):
				stations.append({
					"station_id": f"Bay-{station_num}",
					"station_name": f"Workstation Bay-{station_num}",
					"floor": floor,
					"building": building,
					"distance_from_kitchen": 50 + (station_num * 10),
					"qr_token": f"token-bay-{station_num}-{datetime.now().strftime('%Y%m%d')}",
					"qr_token_expires_at": datetime.now() + timedelta(days=1),
					"is_active": True
				})
				station_num += 1

	for station_data in stations:
		existing = db.query(Station).filter(
			Station.station_id == station_data["station_id"]
		).first()
		if not existing:
			station = Station(**station_data)
			db.add(station)

	logger.info(f"✅ {len(stations)} stations seeded")


def seed_menu_items(db):
	"""Create menu items"""

	menu_items = [
		# Beverages
		{"item_name": "Chai", "category": "Beverages", "price": 30.00,
		 "prep_time_estimate": 3, "complexity_score": 1, "is_available": True},
		{"item_name": "Coffee", "category": "Beverages", "price": 50.00,
		 "prep_time_estimate": 4, "complexity_score": 1, "is_available": True},
		{"item_name": "Fresh Juice", "category": "Beverages", "price": 80.00,
		 "prep_time_estimate": 5, "complexity_score": 1, "is_available": True},
		{"item_name": "Lassi", "category": "Beverages", "price": 60.00,
		 "prep_time_estimate": 4, "complexity_score": 1, "is_available": True},

		# Snacks
		{"item_name": "Samosa", "category": "Snacks", "price": 40.00,
		 "prep_time_estimate": 5, "complexity_score": 1, "is_available": True},
		{"item_name": "Pakora", "category": "Snacks", "price": 50.00,
		 "prep_time_estimate": 6, "complexity_score": 1, "is_available": True},
		{"item_name": "French Fries", "category": "Snacks", "price": 100.00,
		 "prep_time_estimate": 8, "complexity_score": 2, "is_available": True},
		{"item_name": "Spring Roll", "category": "Snacks", "price": 80.00,
		 "prep_time_estimate": 7, "complexity_score": 2, "is_available": True},

		# Sandwiches
		{"item_name": "Club Sandwich", "category": "Sandwiches", "price": 150.00,
		 "prep_time_estimate": 10, "complexity_score": 2, "is_available": True},
		{"item_name": "Chicken Sandwich", "category": "Sandwiches", "price": 120.00,
		 "prep_time_estimate": 8, "complexity_score": 2, "is_available": True},
		{"item_name": "Egg Sandwich", "category": "Sandwiches", "price": 80.00,
		 "prep_time_estimate": 7, "complexity_score": 2, "is_available": True},

		# Main Course
		{"item_name": "Chicken Biryani", "category": "Main Course", "price": 250.00,
		 "prep_time_estimate": 15, "complexity_score": 3, "is_available": True},
		{"item_name": "Beef Biryani", "category": "Main Course", "price": 280.00,
		 "prep_time_estimate": 15, "complexity_score": 3, "is_available": True},
		{"item_name": "Daal Chawal", "category": "Main Course", "price": 150.00,
		 "prep_time_estimate": 12, "complexity_score": 2, "is_available": True},
		{"item_name": "Chicken Karahi", "category": "Main Course", "price": 350.00,
		 "prep_time_estimate": 20, "complexity_score": 3, "is_available": True},
		{"item_name": "Chicken Paratha Roll", "category": "Main Course", "price": 120.00,
		 "prep_time_estimate": 10, "complexity_score": 2, "is_available": True},
		{"item_name": "Thali", "category": "Main Course", "price": 300.00,
		 "prep_time_estimate": 20, "complexity_score": 3, "is_available": True},

		# Desserts
		{"item_name": "Gulab Jamun", "category": "Desserts", "price": 60.00,
		 "prep_time_estimate": 3, "complexity_score": 1, "is_available": True},
		{"item_name": "Kheer", "category": "Desserts", "price": 80.00,
		 "prep_time_estimate": 5, "complexity_score": 1, "is_available": True},
	]

	for item_data in menu_items:
		existing = db.query(MenuItem).filter(
			MenuItem.item_name == item_data["item_name"]
		).first()
		if not existing:
			item = MenuItem(**item_data)
			db.add(item)

	logger.info(f"✅ {len(menu_items)} menu items seeded")


def seed_runners(db):
	"""Create runner detail records"""

	runner_details = [
		{"runner_id": "RUN-001", "current_status": "Available",
		 "active_order_count": 0, "max_capacity": 5},
		{"runner_id": "RUN-002", "current_status": "Available",
		 "active_order_count": 0, "max_capacity": 5},
		{"runner_id": "RUN-003", "current_status": "Available",
		 "active_order_count": 0, "max_capacity": 5},
		{"runner_id": "RUN-004", "current_status": "Available",
		 "active_order_count": 0, "max_capacity": 4},
		{"runner_id": "RUN-005", "current_status": "Available",
		 "active_order_count": 0, "max_capacity": 4},
	]

	for runner_data in runner_details:
		existing = db.query(Runner).filter(
			Runner.runner_id == runner_data["runner_id"]
		).first()
		if not existing:
			runner = Runner(**runner_data)
			db.add(runner)

	logger.info(f"✅ {len(runner_details)} runners seeded")


def seed_trivia_questions(db):
	"""Create trivia questions"""

	questions = [
		{
			"question_text": "What does CPU stand for?",
			"option_a": "Central Processing Unit",
			"option_b": "Computer Personal Unit",
			"option_c": "Central Program Utility",
			"option_d": "Computer Processing Unit",
			"correct_option": "A",
			"category": "Tech",
			"difficulty": "Easy"
		},
		{
			"question_text": "Which programming language is known as the 'language of the web'?",
			"option_a": "Python",
			"option_b": "JavaScript",
			"option_c": "Java",
			"option_d": "C++",
			"correct_option": "B",
			"category": "Tech",
			"difficulty": "Easy"
		},
		{
			"question_text": "What does HTML stand for?",
			"option_a": "Hyper Text Markup Language",
			"option_b": "High Tech Modern Language",
			"option_c": "Hyper Transfer Markup Language",
			"option_d": "Home Tool Markup Language",
			"correct_option": "A",
			"category": "Tech",
			"difficulty": "Easy"
		},
		{
			"question_text": "What is the speed of light approximately?",
			"option_a": "300,000 km/s",
			"option_b": "150,000 km/s",
			"option_c": "500,000 km/s",
			"option_d": "1,000,000 km/s",
			"correct_option": "A",
			"category": "Science",
			"difficulty": "Medium"
		},
		{
			"question_text": "Which data structure uses FIFO?",
			"option_a": "Stack",
			"option_b": "Queue",
			"option_c": "Tree",
			"option_d": "Graph",
			"correct_option": "B",
			"category": "Tech",
			"difficulty": "Medium"
		},
		{
			"question_text": "What is the time complexity of binary search?",
			"option_a": "O(n)",
			"option_b": "O(n²)",
			"option_c": "O(log n)",
			"option_d": "O(1)",
			"correct_option": "C",
			"category": "Tech",
			"difficulty": "Medium"
		},
		{
			"question_text": "What does API stand for?",
			"option_a": "Application Programming Interface",
			"option_b": "Application Process Integration",
			"option_c": "Automated Programming Interface",
			"option_d": "Application Protocol Interface",
			"correct_option": "A",
			"category": "Tech",
			"difficulty": "Easy"
		},
		{
			"question_text": "Which planet is known as the Red Planet?",
			"option_a": "Venus",
			"option_b": "Jupiter",
			"option_c": "Mars",
			"option_d": "Saturn",
			"correct_option": "C",
			"category": "Science",
			"difficulty": "Easy"
		},
		{
			"question_text": "What is the chemical formula for water?",
			"option_a": "CO2",
			"option_b": "H2O",
			"option_c": "NaCl",
			"option_d": "O2",
			"correct_option": "B",
			"category": "Science",
			"difficulty": "Easy"
		},
		{
			"question_text": "In Python, which keyword is used to define a function?",
			"option_a": "function",
			"option_b": "func",
			"option_c": "def",
			"option_d": "define",
			"correct_option": "C",
			"category": "Tech",
			"difficulty": "Easy"
		},
	]

	for q_data in questions:
		existing = db.query(TriviaQuestion).filter(
			TriviaQuestion.question_text == q_data["question_text"]
		).first()
		if not existing:
			question = TriviaQuestion(**q_data)
			db.add(question)

	logger.info(f"✅ {len(questions)} trivia questions seeded")


# ============================================
# RUN SEED
# ============================================
if __name__ == "__main__":
	print("🌱 Seeding database...")
	seed_all()
	print("✅ Done!")

