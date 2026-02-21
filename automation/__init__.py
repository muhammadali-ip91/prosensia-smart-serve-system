"""
ProSensia Smart-Serve Automation Module
========================================
Provides load testing, data generation, simulation,
and stress testing capabilities for the ProSensia system.

Sub-modules:
- load_testing:     Simulate concurrent users and measure performance
- data_generation:  Seed database with realistic test data
- simulation:       Simulate complete order lifecycle flows
- reports:          Generate test reports

Usage:
	python -m automation.load_testing.load_simulator
	python -m automation.data_generation.seed_all
	python -m automation.simulation.order_flow_simulator
"""

__version__ = "1.0.0"
__author__ = "ProSensia Team"
