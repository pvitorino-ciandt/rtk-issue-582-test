"""Minimal test file demonstrating the pytest skipif bug.

This file can be run standalone with: pytest test_example.py

When CI environment variable is set, the test should skip but instead fails with:
    NameError: name 'true' is not defined

This is because GitHub Actions sets CI=true (string), and pytest tries to
evaluate the string "true" as Python code.
"""
import os

import pytest


# This class has the BUG - missing bool() wrapper
@pytest.mark.skipif(
    os.getenv("CI"),
    reason="Skip in CI environment",
)
class TestWithBug:
    """Test class with buggy skipif condition."""

    def test_example_one(self) -> None:
        """Example test that should skip in CI."""
        assert 1 + 1 == 2

    def test_example_two(self) -> None:
        """Another test that should skip in CI."""
        assert "hello" == "hello"

    def test_example_three(self) -> None:
        """Third test that should skip in CI."""
        assert len([1, 2, 3]) == 3


# This class has the FIX - correct bool() wrapper
@pytest.mark.skipif(
    bool(os.getenv("CI")),
    reason="Skip in CI environment",
)
class TestWithFix:
    """Test class with correct skipif condition."""

    def test_example_one(self) -> None:
        """Example test that correctly skips in CI."""
        assert 1 + 1 == 2

    def test_example_two(self) -> None:
        """Another test that correctly skips in CI."""
        assert "hello" == "hello"

    def test_example_three(self) -> None:
        """Third test that correctly skips in CI."""
        assert len([1, 2, 3]) == 3
