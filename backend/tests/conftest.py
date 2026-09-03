"""
AI Tutor — Test Configuration.

Shared fixtures for all tests.
"""

import sys
from pathlib import Path

import pytest

# Ensure backend is on the Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
