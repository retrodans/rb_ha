"""Pytest configuration and fixtures for Fenix V24 integration tests.

This file provides common fixtures and configuration for all tests, including:
- Test credentials (loaded from environment or test config)
- Mock objects for unit tests
- Shared test data
"""
import os
import pytest
from unittest.mock import Mock, patch


# Test credentials - can be set via environment variables or test config
TEST_EMAIL = os.getenv("FENIX_TEST_EMAIL", "test@example.com")
TEST_PASSWORD = os.getenv("FENIX_TEST_PASSWORD", "test_password")
TEST_SMARTHOME_ID = os.getenv("FENIX_TEST_SMARTHOME_ID", "TEST_SMARTHOME_ID")


@pytest.fixture
def test_credentials():
    """Provide test credentials for API tests.

    Returns:
        dict: Test credentials with email, password, and smarthome_id
    """
    return {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "smarthome_id": TEST_SMARTHOME_ID,
    }


@pytest.fixture
def mock_auth_response():
    """Mock successful authentication response from Keycloak.

    Returns:
        dict: Mock OAuth2 token response
    """
    return {
        "access_token": "mock_access_token_12345",
        "refresh_token": "mock_refresh_token_12345",
        "expires_in": 3600,
        "token_type": "Bearer",
    }


@pytest.fixture
def mock_zones_response():
    """Mock successful zones response from Fenix V24 API.

    Returns:
        dict: Mock zones data with sample zones
    """
    return {
        "data": {
            "zones": [
                {
                    "zone_id": "zone_1",
                    "zone_label": "Living Room",
                    "devices": [
                        {
                            "device_id": "device_1",
                            "temperature_air": 720,  # 72.0°F = 22.2°C
                        }
                    ],
                },
                {
                    "zone_id": "zone_2",
                    "zone_label": "Bedroom",
                    "devices": [
                        {
                            "device_id": "device_2",
                            "temperature_air": 680,  # 68.0°F = 20.0°C
                        }
                    ],
                },
            ]
        }
    }


@pytest.fixture
def mock_empty_zones_response():
    """Mock zones response with no zones.

    Returns:
        dict: Empty zones response
    """
    return {"data": {"zones": []}}


@pytest.fixture
def mock_requests_session():
    """Mock requests session for API calls.

    Yields:
        Mock: Mocked requests.post function
    """
    with patch("requests.post") as mock_post:
        yield mock_post


@pytest.fixture
def real_api_available():
    """Check if real API credentials are available for integration tests.

    Returns:
        bool: True if real credentials are available
    """
    return (
        TEST_EMAIL != "test@example.com"
        and TEST_PASSWORD != "test_password"
        and TEST_SMARTHOME_ID != "TEST_SMARTHOME_ID"
    )


# Pytest markers for different test types
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (requires real API credentials)"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test (uses mocks, no real API calls)"
    )
