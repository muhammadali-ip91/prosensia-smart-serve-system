"""
Main Load Simulator
=====================
The primary load testing script that simulates 100 virtual
engineers placing 1000+ orders concurrently.

This is the MAIN automation script referenced in the proposal.

Features:
1. 100 virtual engineers placing orders
2. 10 orders per engineer (1000 total)
3. Mix of Urgent (20%) and Regular (80%)
4. Simulates peak and off-peak patterns
5. Generates AI training data
6. Produces comprehensive load test report

Usage:
	python -m automation.load_testing.load_simulator
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config
from automation.load_testing.report_generator import (
	generate_report,
)
from automation.simulation.order_flow_simulator import (
	OrderFlowSimulator,
)


def run_load_test(
	num_engineers: int = None,
	orders_per_engineer: int = None,
	max_workers: int = None,
	save_report: bool = True,
) -> dict:
	"""
	Run the complete load test.
    
	Args:
		num_engineers: Number of virtual engineers.
		orders_per_engineer: Orders per engineer.
		max_workers: Thread pool size.
		save_report: Whether to save report to file.
    
	Returns:
		Complete results dictionary.
	"""
	if num_engineers is None:
		num_engineers = Config.TOTAL_ENGINEERS
	if orders_per_engineer is None:
		orders_per_engineer = Config.ORDERS_PER_ENGINEER
	if max_workers is None:
		max_workers = Config.THREAD_POOL_SIZE

	total_orders = num_engineers * orders_per_engineer

	print()
	print("╔" + "═" * 58 + "╗")
	print("║" + " ProSensia Smart-Serve".center(58) + "║")
	print("║" + " LOAD TEST".center(58) + "║")
	print("╠" + "═" * 58 + "╣")
	print(f"║  Engineers:         {num_engineers:<37}║")
	print(f"║  Orders/Engineer:   {orders_per_engineer:<37}║")
	print(f"║  Total Orders:      {total_orders:<37}║")
	print(f"║  Max Workers:       {max_workers:<37}║")
	print(f"║  Urgent %:          {Config.URGENT_ORDER_PERCENTAGE}%{' '*34}║")
	print(f"║  API URL:           {Config.BASE_URL:<37}║")
	print(
		f"║  Started:           "
		f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<37}║"
	)
	print("╚" + "═" * 58 + "╝")

	# Run the simulation
	simulator = OrderFlowSimulator(base_url=Config.BASE_URL)
	results = simulator.run(
		num_engineers=num_engineers,
		orders_per_engineer=orders_per_engineer,
		max_workers=max_workers,
	)

	# Generate report
	if save_report:
		report = generate_report(results)

		# Save report to file
		os.makedirs(Config.REPORT_DIR, exist_ok=True)
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		report_path = os.path.join(
			Config.REPORT_DIR,
			f"load_test_report_{timestamp}.txt"
		)

		with open(report_path, "w", encoding="utf-8") as f:
			f.write(report)

		print(f"\n📄 Report saved to: {report_path}")

		# Also save raw results as JSON
		json_path = os.path.join(
			Config.REPORT_DIR,
			f"load_test_results_{timestamp}.json"
		)

		# Remove non-serializable data
		json_results = {
			k: v for k, v in results.items()
			if k != "order_details"
		}
		json_results["order_count"] = len(
			results.get("order_details", [])
		)

		with open(json_path, "w") as f:
			json.dump(json_results, f, indent=2, default=str)

		print(f"📊 Raw results saved to: {json_path}")

	return results


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(
		description="ProSensia Load Test"
	)
	parser.add_argument(
		"--engineers", type=int, default=None,
		help="Number of virtual engineers"
	)
	parser.add_argument(
		"--orders", type=int, default=None,
		help="Orders per engineer"
	)
	parser.add_argument(
		"--workers", type=int, default=None,
		help="Max concurrent workers"
	)
	parser.add_argument(
		"--quick", action="store_true",
		help="Quick test (10 engineers, 3 orders each)"
	)

	args = parser.parse_args()

	if args.quick:
		run_load_test(
			num_engineers=10,
			orders_per_engineer=3,
			max_workers=5,
		)
	else:
		run_load_test(
			num_engineers=args.engineers,
			orders_per_engineer=args.orders,
			max_workers=args.workers,
		)
