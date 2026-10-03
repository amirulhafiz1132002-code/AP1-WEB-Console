"""
Pytest Configuration - Centralized test configuration and setup
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.fixtures import *
from tests.utils import TestLogger, PerformanceTracker

_performance_tracker = PerformanceTracker()


def pytest_configure(config):
    """Configure pytest markers."""
    for marker in (
        "integration: mark test as integration test",
        "unit: mark test as unit test",
        "slow: mark test as slow running",
        "ai_system: mark test as AI system test",
    ):
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(config, items):
    """Mark tests by location and deselect slow tests by default."""
    deselected = []
    selected = []
    run_slow = config.getoption("--run-slow")

    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        if not run_slow and item.get_closest_marker("slow"):
            deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


@pytest.fixture
def performance_tracker():
    return _performance_tracker


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        if rep.passed:
            TestLogger.log_test_end(item.name, "PASSED ✅")
        elif rep.failed:
            TestLogger.log_test_end(item.name, "FAILED ❌")
        elif rep.skipped:
            TestLogger.log_test_end(item.name, "SKIPPED ⏭️")


class TestContext:
    def __init__(self, test_name: str):
        self.test_name = test_name

    def __enter__(self):
        TestLogger.log_test_start(self.test_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            TestLogger.log_test_end(self.test_name, "PASSED ✅")
        else:
            TestLogger.log_error(f"Test {self.test_name} failed", exc_val)


@pytest.fixture
def test_context():
    return TestContext


def pytest_addoption(parser):
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="run slow tests",
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


__all__ = [
    "performance_tracker",
    "pytest_configure",
    "pytest_collection_modifyitems",
    "pytest_runtest_makereport",
    "pytest_addoption",
    "TestContext",
]
