"""
Seed Trivia Questions Script
==============================
Generates tech trivia questions for the engagement module.

Usage:
	python -m automation.data_generation.seed_trivia
"""

import sys
import os
import random
import requests
from typing import List, Dict

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config


TRIVIA_QUESTIONS = [
	# Tech - Easy
	{
		"question_text": "What does CPU stand for?",
		"option_a": "Central Processing Unit",
		"option_b": "Central Program Utility",
		"option_c": "Computer Personal Unit",
		"option_d": "Central Processor Unifier",
		"correct_option": "A",
		"category": "Tech",
		"difficulty": "Easy",
	},
	{
		"question_text": "What does HTML stand for?",
		"option_a": "Hyper Text Markup Language",
		"option_b": "High Tech Modern Language",
		"option_c": "Hyper Transfer Markup Language",
		"option_d": "Home Tool Markup Language",
		"correct_option": "A",
		"category": "Tech",
		"difficulty": "Easy",
	},
	{
		"question_text": "Which company developed Python?",
		"option_a": "Microsoft",
		"option_b": "Google",
		"option_c": "Guido van Rossum",
		"option_d": "Apple",
		"correct_option": "C",
		"category": "Tech",
		"difficulty": "Easy",
	},
	{
		"question_text": "What is the binary representation of 10?",
		"option_a": "1010",
		"option_b": "1100",
		"option_c": "1001",
		"option_d": "1110",
		"correct_option": "A",
		"category": "Tech",
		"difficulty": "Easy",
	},
	{
		"question_text": "RAM stands for?",
		"option_a": "Read Access Memory",
		"option_b": "Random Access Memory",
		"option_c": "Run Access Memory",
		"option_d": "Random Allocation Memory",
		"correct_option": "B",
		"category": "Tech",
		"difficulty": "Easy",
	},
	{
		"question_text": "Which key is used to copy in Windows?",
		"option_a": "Ctrl + V",
		"option_b": "Ctrl + X",
		"option_c": "Ctrl + C",
		"option_d": "Ctrl + Z",
		"correct_option": "C",
		"category": "Tech",
		"difficulty": "Easy",
	},
	{
		"question_text": "What does USB stand for?",
		"option_a": "Universal Serial Bus",
		"option_b": "United Serial Bus",
		"option_c": "Universal System Bus",
		"option_d": "Unified Serial Block",
		"correct_option": "A",
		"category": "Tech",
		"difficulty": "Easy",
	},

	# Tech - Medium
	{
		"question_text": "What is the time complexity of binary search?",
		"option_a": "O(n)",
		"option_b": "O(log n)",
		"option_c": "O(n²)",
		"option_d": "O(1)",
		"correct_option": "B",
		"category": "Tech",
		"difficulty": "Medium",
	},
	{
		"question_text": "Which protocol is used for secure web browsing?",
		"option_a": "HTTP",
		"option_b": "FTP",
		"option_c": "HTTPS",
		"option_d": "SMTP",
		"correct_option": "C",
		"category": "Tech",
		"difficulty": "Medium",
	},
	{
		"question_text": "What does API stand for?",
		"option_a": "Application Programming Interface",
		"option_b": "Applied Program Integration",
		"option_c": "Automated Programming Interface",
		"option_d": "Application Process Integration",
		"correct_option": "A",
		"category": "Tech",
		"difficulty": "Medium",
	},
	{
		"question_text": "Which data structure uses FIFO?",
		"option_a": "Stack",
		"option_b": "Queue",
		"option_c": "Tree",
		"option_d": "Graph",
		"correct_option": "B",
		"category": "Tech",
		"difficulty": "Medium",
	},
	{
		"question_text": "What is Docker used for?",
		"option_a": "Database management",
		"option_b": "Containerization",
		"option_c": "Web design",
		"option_d": "Email service",
		"correct_option": "B",
		"category": "Tech",
		"difficulty": "Medium",
	},
	{
		"question_text": "Which database is NoSQL?",
		"option_a": "PostgreSQL",
		"option_b": "MySQL",
		"option_c": "MongoDB",
		"option_d": "SQLite",
		"correct_option": "C",
		"category": "Tech",
		"difficulty": "Medium",
	},
	{
		"question_text": "JWT stands for?",
		"option_a": "Java Web Token",
		"option_b": "JSON Web Token",
		"option_c": "JavaScript Web Transfer",
		"option_d": "JSON Webpage Token",
		"correct_option": "B",
		"category": "Tech",
		"difficulty": "Medium",
	},

	# Tech - Hard
	{
		"question_text": "What is the CAP theorem about?",
		"option_a": "CPU Architecture",
		"option_b": "Distributed Systems tradeoffs",
		"option_c": "Compiler optimization",
		"option_d": "Cache replacement",
		"correct_option": "B",
		"category": "Tech",
		"difficulty": "Hard",
	},
	{
		"question_text": "What is eventual consistency?",
		"option_a": "All nodes always have same data",
		"option_b": "Data is consistent only on restart",
		"option_c": "Given enough time all replicas converge",
		"option_d": "Consistency is never achieved",
		"correct_option": "C",
		"category": "Tech",
		"difficulty": "Hard",
	},
	{
		"question_text": "What is a race condition?",
		"option_a": "Fast program execution",
		"option_b": "Multiple threads accessing shared resource unpredictably",
		"option_c": "Network speed issue",
		"option_d": "CPU clock speed mismatch",
		"correct_option": "B",
		"category": "Tech",
		"difficulty": "Hard",
	},

	# Science - Easy
	{
		"question_text": "What is the chemical symbol for water?",
		"option_a": "H2O",
		"option_b": "CO2",
		"option_c": "O2",
		"option_d": "NaCl",
		"correct_option": "A",
		"category": "Science",
		"difficulty": "Easy",
	},
	{
		"question_text": "How many planets are in our solar system?",
		"option_a": "7",
		"option_b": "8",
		"option_c": "9",
		"option_d": "10",
		"correct_option": "B",
		"category": "Science",
		"difficulty": "Easy",
	},
	{
		"question_text": "What gas do plants absorb?",
		"option_a": "Oxygen",
		"option_b": "Nitrogen",
		"option_c": "Carbon Dioxide",
		"option_d": "Hydrogen",
		"correct_option": "C",
		"category": "Science",
		"difficulty": "Easy",
	},
	{
		"question_text": "What is the speed of light approximately?",
		"option_a": "3 × 10⁸ m/s",
		"option_b": "3 × 10⁶ m/s",
		"option_c": "3 × 10¹⁰ m/s",
		"option_d": "3 × 10⁴ m/s",
		"correct_option": "A",
		"category": "Science",
		"difficulty": "Easy",
	},

	# Science - Medium
	{
		"question_text": "What is Newton's second law?",
		"option_a": "F = mv",
		"option_b": "F = ma",
		"option_c": "E = mc²",
		"option_d": "F = mg",
		"correct_option": "B",
		"category": "Science",
		"difficulty": "Medium",
	},
	{
		"question_text": "What is the atomic number of Carbon?",
		"option_a": "4",
		"option_b": "6",
		"option_c": "8",
		"option_d": "12",
		"correct_option": "B",
		"category": "Science",
		"difficulty": "Medium",
	},

	# Logic - Easy
	{
		"question_text": "What comes next: 2, 4, 8, 16, ?",
		"option_a": "24",
		"option_b": "30",
		"option_c": "32",
		"option_d": "36",
		"correct_option": "C",
		"category": "Logic",
		"difficulty": "Easy",
	},
	{
		"question_text": "If A=1, B=2, C=3, what is D+E?",
		"option_a": "7",
		"option_b": "8",
		"option_c": "9",
		"option_d": "10",
		"correct_option": "C",
		"category": "Logic",
		"difficulty": "Easy",
	},

	# Logic - Medium
	{
		"question_text": "How many squares are on a chess board?",
		"option_a": "64",
		"option_b": "128",
		"option_c": "204",
		"option_d": "32",
		"correct_option": "C",
		"category": "Logic",
		"difficulty": "Medium",
	},
	{
		"question_text": "What is 15% of 200?",
		"option_a": "25",
		"option_b": "30",
		"option_c": "35",
		"option_d": "40",
		"correct_option": "B",
		"category": "Logic",
		"difficulty": "Medium",
	},

	# Logic - Hard
	{
		"question_text": "A bat and ball cost ₹110. Bat costs ₹100 more than ball. Ball costs?",
		"option_a": "₹10",
		"option_b": "₹5",
		"option_c": "₹15",
		"option_d": "₹20",
		"correct_option": "B",
		"category": "Logic",
		"difficulty": "Hard",
	},
]


def generate_trivia_data() -> List[Dict]:
	"""Return all trivia questions."""
	return TRIVIA_QUESTIONS


def seed_trivia_via_api(
	base_url: str = None,
	admin_token: str = None,
) -> Dict:
	"""Seed trivia questions via API."""
	if base_url is None:
		base_url = Config.BASE_URL

	questions = generate_trivia_data()
	print(f"Seeding {len(questions)} trivia questions...")

	if admin_token is None:
		try:
			response = requests.post(
				f"{base_url}/auth/login",
				json={
					"employee_id": "ADM-001",
					"password": Config.ADMIN_PASSWORD,
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			admin_token = response.json()["access_token"]
		except Exception as e:
			print(f"Admin login failed: {e}")
			return {"success": 0, "failed": len(questions)}

	results = {
		"total": len(questions),
		"success": 0,
		"failed": 0,
	}

	for q in questions:
		try:
			response = requests.post(
				f"{base_url}/admin/trivia",
				json=q,
				headers={
					"Authorization": f"Bearer {admin_token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			if response.status_code in (200, 201, 409):
				results["success"] += 1
			else:
				results["failed"] += 1
		except Exception:
			results["failed"] += 1

	print(
		f"Trivia: ✅ {results['success']} "
		f"❌ {results['failed']}"
	)

	# Print category breakdown
	categories = {}
	for q in questions:
		cat = q["category"]
		diff = q["difficulty"]
		key = f"{cat}-{diff}"
		categories[key] = categories.get(key, 0) + 1

	print("\nCategory breakdown:")
	for key, count in sorted(categories.items()):
		print(f"  {key}: {count}")

	return results


if __name__ == "__main__":
	print("=" * 50)
	print("  ProSensia - Seed Trivia Questions")
	print("=" * 50)

	questions = generate_trivia_data()
	print(f"\nTotal questions: {len(questions)}")

	categories = {}
	for q in questions:
		key = f"{q['category']} ({q['difficulty']})"
		categories[key] = categories.get(key, 0) + 1

	for key, count in sorted(categories.items()):
		print(f"  {key}: {count}")
