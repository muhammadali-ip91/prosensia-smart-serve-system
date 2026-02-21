"""
Report Generator
==================
Generates comprehensive load test reports from simulation results.

Usage:
	Called by load_simulator.py after test completion.
"""

from datetime import datetime
from typing import Dict


def generate_report(results: Dict) -> str:
	"""
	Generate a formatted load test report.
    
	Args:
		results: Results dictionary from OrderFlowSimulator.
    
	Returns:
		Formatted report string.
	"""
	r = results

	total = r.get("total_orders", 0)
	successful = r.get("successful", 0)
	failed = r.get("failed", 0)
	cancelled = r.get("cancelled", 0)
	success_rate = (
		(successful / total * 100) if total > 0 else 0
	)

	report = []
	report.append("=" * 60)
	report.append("  PROSENSIA SMART-SERVE")
	report.append("  LOAD TEST REPORT")
	report.append("=" * 60)
	report.append(
		f"  Generated: {datetime.now().isoformat()}"
	)
	report.append("")

	# Order Statistics
	report.append("─" * 60)
	report.append("  ORDER STATISTICS")
	report.append("─" * 60)
	report.append(f"  Total Orders Placed:     {total:>10}")
	report.append(f"  Successful Orders:       {successful:>10}")
	report.append(f"  Failed Orders:           {failed:>10}")
	report.append(f"  Cancelled Orders:        {cancelled:>10}")
	report.append(f"  Success Rate:            {success_rate:>9.1f}%")
	report.append("")

	# API Performance
	report.append("─" * 60)
	report.append("  API PERFORMANCE")
	report.append("─" * 60)
	report.append(
		f"  Average Response Time:   "
		f"{r.get('avg_response_time_ms', 0):>8.1f}ms"
	)
	report.append(
		f"  Min Response Time:       "
		f"{r.get('min_response_time_ms', 0):>8.1f}ms"
	)
	report.append(
		f"  Max Response Time:       "
		f"{r.get('max_response_time_ms', 0):>8.1f}ms"
	)
	report.append(
		f"  P50 (Median):            "
		f"{r.get('p50_response_ms', 0):>8.1f}ms"
	)
	report.append(
		f"  P95:                     "
		f"{r.get('p95_response_ms', 0):>8.1f}ms"
	)
	report.append(
		f"  P99:                     "
		f"{r.get('p99_response_ms', 0):>8.1f}ms"
	)
	report.append("")

	# Delivery Stats
	if r.get("avg_delivery_time_min"):
		report.append("─" * 60)
		report.append("  DELIVERY STATISTICS")
		report.append("─" * 60)
		report.append(
			f"  Avg Delivery Time:       "
			f"{r['avg_delivery_time_min']:>8.1f}s"
		)
		report.append("")

	# API Call Count
	api_calls = len(r.get("api_response_times", []))
	report.append("─" * 60)
	report.append("  SYSTEM LOAD")
	report.append("─" * 60)
	report.append(f"  Total API Calls Made:    {api_calls:>10}")
	report.append(
		f"  Total Test Duration:     "
		f"{r.get('total_time_seconds', 0):>8.1f}s"
	)
	if r.get("total_time_seconds", 0) > 0:
		rps = api_calls / r["total_time_seconds"]
		report.append(
			f"  Requests Per Second:     {rps:>9.1f}"
		)
	report.append("")

	# Errors
	errors = r.get("errors", [])
	if errors:
		report.append("─" * 60)
		report.append(f"  ERRORS ({len(errors)} total)")
		report.append("─" * 60)

		# Group errors by type
		error_types = {}
		for error in errors:
			# Extract error type
			if "Login failed" in error:
				key = "Login Failed"
			elif "Timeout" in error or "timeout" in error:
				key = "Timeout"
			elif "Connection" in error:
				key = "Connection Error"
			elif "500" in error:
				key = "Server Error (500)"
			elif "429" in error:
				key = "Rate Limited (429)"
			else:
				key = "Other"
			error_types[key] = error_types.get(key, 0) + 1

		for error_type, count in sorted(
			error_types.items(), key=lambda x: -x[1]
		):
			report.append(f"  - {error_type}: {count}")
		report.append("")

	# Recommendations
	report.append("─" * 60)
	report.append("  RECOMMENDATIONS")
	report.append("─" * 60)

	if success_rate >= 99:
		report.append(
			"  ✅ Excellent: System handles load well"
		)
	elif success_rate >= 95:
		report.append(
			"  ⚠️  Good: Minor issues under load"
		)
	else:
		report.append(
			"  ❌ Needs Improvement: Significant failures"
		)

	avg_rt = r.get("avg_response_time_ms", 0)
	if avg_rt < 200:
		report.append(
			"  ✅ API response times are within target (<200ms)"
		)
	elif avg_rt < 500:
		report.append(
			"  ⚠️  API response times are acceptable (<500ms)"
		)
	else:
		report.append(
			"  ❌ API response times need optimization (>500ms)"
		)

	p95 = r.get("p95_response_ms", 0)
	if p95 < 500:
		report.append(
			"  ✅ P95 latency is good (<500ms)"
		)
	elif p95 < 1000:
		report.append(
			"  ⚠️  P95 latency is acceptable (<1000ms)"
		)
	else:
		report.append(
			"  ❌ P95 latency needs investigation (>1000ms)"
		)

	if failed > 0:
		report.append(
			f"  ⚠️  Investigate {failed} failed orders"
		)

	report.append("")
	report.append("=" * 60)
	report.append("  END OF REPORT")
	report.append("=" * 60)

	return "\n".join(report)
