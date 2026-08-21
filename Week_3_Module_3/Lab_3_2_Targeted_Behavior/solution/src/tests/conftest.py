"""Shared test helpers for the NorthPeak test suite."""

from __future__ import annotations

import pytest

TEST_TOKEN_PREFIX = "npk_test_"


def make_test_token(suffix: str = "abc123456") -> str:
    """Return an obviously-fake token with a valid shape.

    Produces a token that satisfies verify_token (``npk_`` prefix, >= 12
    characters) without weakening the check itself. Never use a real
    credential here.
    """
    return f"{TEST_TOKEN_PREFIX}{suffix}"


@pytest.fixture
def good_token() -> str:
    """A valid-shaped fake token for tests that just need one to pass auth."""
    return make_test_token()
