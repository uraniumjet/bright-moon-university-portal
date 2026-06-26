"""
Shared pytest fixtures for the Bright Moon University Portal.
"""

import pytest

from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def client():
    """
    Creates a reusable FastAPI test client.
    """
    return TestClient(app)