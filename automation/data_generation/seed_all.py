"""
Seed All Data Script
======================
Runs all seed scripts together to populate the entire system.

Usage:
	python -m automation.data_generation.seed_all
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config
from automation.data_generation.seed_engineers import (
	generate_engineer_data,
	seed_engineers_via_api,
	seed_engineers_direct,
)
from automation.data_generation.seed_menu import (
	generate_menu_data,
	seed_menu_via_api,
)
from automation.data_generation.seed_stations import (
	generate_station_data,
	seed_stations_via_api,
)
from automation.data_generation.seed_runners import (
	generate_runner_data,
	seed_runners_via_api,
)
from automation.data_generation.seed_trivia import (
	generate_trivia_data,
	seed_trivia_via_api,
)


def seed_all(
	mode: str = "generate",
	base_url: str = None,
) -> dict:
	"""
	Run all seed scripts.
    
	Args:
		mode: 'generate' = just generate data and print
			  'api' = seed via API calls
		base_url: API base URL (only needed for 'api' mode).
    
	Returns:
		Summary of all seeding operations.
	"""
	if base_url is None:
		base_url = Config.BASE_URL

	print("=" * 60)
	print("  ProSensia Smart-Serve")
	print("  Complete Data Seeding")
	print("=" * 60)
	print(f"\nMode: {mode}")
	print(f"Started at: {datetime.now().isoformat()}")

	Config.print_config()

	summary = {}
	start_time = time.time()

	if mode == "api":
		# Seed via API calls
		print("\n" + "─" * 60)
		print("  1/5: Seeding Stations...")
		print("─" * 60)
		summary["stations"] = seed_stations_via_api(base_url)

		print("\n" + "─" * 60)
		print("  2/5: Seeding Menu Items...")
		print("─" * 60)
		summary["menu"] = seed_menu_via_api(base_url)

		print("\n" + "─" * 60)
		print("  3/5: Seeding Engineers...")
		print("─" * 60)
		summary["engineers"] = seed_engineers_via_api(
			base_url=base_url
		)

		print("\n" + "─" * 60)
		print("  4/5: Seeding Runners...")
		print("─" * 60)
		summary["runners"] = seed_runners_via_api(base_url)

		print("\n" + "─" * 60)
		print("  5/5: Seeding Trivia Questions...")
		print("─" * 60)
		summary["trivia"] = seed_trivia_via_api(base_url)

	else:
		# Just generate and display data
		print("\n1/5: Generating Stations...")
		stations = generate_station_data()
		summary["stations"] = {"total": len(stations), "generated": True}
		print(f"  Generated {len(stations)} stations")

		print("\n2/5: Generating Menu Items...")
		menu = generate_menu_data()
		summary["menu"] = {"total": len(menu), "generated": True}
		print(f"  Generated {len(menu)} menu items")

		print("\n3/5: Generating Engineers...")
		engineers = generate_engineer_data()
		summary["engineers"] = {
			"total": len(engineers), "generated": True
		}
		print(f"  Generated {len(engineers)} engineers")

		print("\n4/5: Generating Runners...")
		runners = generate_runner_data()
		summary["runners"] = {
			"total": len(runners), "generated": True
		}
		print(f"  Generated {len(runners)} runners")

		print("\n5/5: Generating Trivia Questions...")
		trivia = generate_trivia_data()
		summary["trivia"] = {
			"total": len(trivia), "generated": True
		}
		print(f"  Generated {len(trivia)} trivia questions")

	elapsed = time.time() - start_time

	# Print summary
	print("\n" + "=" * 60)
	print("  SEEDING SUMMARY")
	print("=" * 60)
	for entity, result in summary.items():
		total = result.get("total", 0)
		success = result.get("success", total)
		failed = result.get("failed", 0)
		print(f"  {entity:15s}: {total:>5d} total "
			  f"| ✅ {success:>4d} | ❌ {failed:>3d}")
	print(f"\n  Time elapsed: {elapsed:.2f} seconds")
	print(f"  Completed at: {datetime.now().isoformat()}")
	print("=" * 60)

	return summary


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(
		description="Seed all ProSensia data"
	)
	parser.add_argument(
		"--mode",
		choices=["generate", "api"],
		default="generate",
		help="'generate' to just create data, "
			 "'api' to seed via API",
	)
	parser.add_argument(
		"--url",
		default=None,
		help="API base URL",
	)

	args = parser.parse_args()
	seed_all(mode=args.mode, base_url=args.url)
