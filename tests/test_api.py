"""Tests for Fenix V24 API client.

This module contains both unit tests (using mocks) and integration tests
(using real API credentials) for the FenixV24API class.

Run unit tests only:
    pytest tests/test_api.py -m unit

Run integration tests only (requires real credentials):
    pytest tests/test_api.py -m integration

Run all tests:
    pytest tests/test_api.py
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

import sys
import os

# Add the custom_components directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components", "fenix_v24_standalone"))

from api import FenixV24API
from const import TOKEN_ENDPOINT, API_BASE


class TestFenixV24APIUnit:
    """Unit tests for FenixV24API class using mocks."""

    @pytest.mark.unit
    def test_api_initialization(self, test_credentials):
        """Test that API client initializes correctly."""
        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )

        assert api._email == test_credentials["email"]
        assert api._password == test_credentials["password"]
        assert api._smarthome_id == test_credentials["smarthome_id"]
        assert api._access_token is None
        assert api._refresh_token is None
        assert api._token_expires_at is None

    @pytest.mark.unit
    def test_authenticate_success(self, test_credentials, mock_auth_response, mock_requests_session):
        """Test successful authentication."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_auth_response
        mock_requests_session.return_value = mock_response

        # Create API client and authenticate
        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )
        api.authenticate()

        # Verify token was stored
        assert api._access_token == mock_auth_response["access_token"]
        assert api._refresh_token == mock_auth_response["refresh_token"]
        assert api._token_expires_at is not None
        assert api._token_expires_at > datetime.now()

        # Verify API was called correctly
        mock_requests_session.assert_called_once()
        call_args = mock_requests_session.call_args
        assert call_args[0][0] == TOKEN_ENDPOINT
        assert call_args[1]["data"]["username"] == test_credentials["email"]
        assert call_args[1]["data"]["password"] == test_credentials["password"]

    @pytest.mark.unit
    def test_authenticate_failure(self, test_credentials, mock_requests_session):
        """Test authentication failure with invalid credentials."""
        # Setup mock response for failure
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid credentials"
        mock_requests_session.return_value = mock_response

        # Create API client and attempt authentication
        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )

        # Should raise exception on auth failure
        with pytest.raises(Exception, match="Authentication failed"):
            api.authenticate()

    @pytest.mark.unit
    def test_authenticate_uses_cached_token(self, test_credentials, mock_auth_response, mock_requests_session):
        """Test that cached token is reused when still valid."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_auth_response
        mock_requests_session.return_value = mock_response

        # Create API client and authenticate
        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )
        api.authenticate()

        # Reset mock to count calls
        mock_requests_session.reset_mock()

        # Authenticate again - should use cached token
        api.authenticate()

        # Should NOT have made another API call
        mock_requests_session.assert_not_called()

    @pytest.mark.unit
    def test_get_zones_success(self, test_credentials, mock_zones_response, mock_requests_session):
        """Test successful retrieval of zones."""
        # Setup API client with token
        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )
        api._access_token = "mock_token"

        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_zones_response
        mock_requests_session.return_value = mock_response

        # Get zones (returns list of tuples: [(zone_id, zone_data), ...])
        zones = api.get_zones()

        # Verify zones were returned as tuples
        assert len(zones) == 2
        assert zones[0][0] == "1"  # zone_id (from num_zone field)
        assert zones[0][1]["zone_label"] == "Living Room"  # zone_data
        assert zones[1][0] == "2"
        assert zones[1][1]["zone_label"] == "Bedroom"

        # Verify API was called correctly
        call_args = mock_requests_session.call_args
        assert API_BASE in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer mock_token"
        assert call_args[1]["data"]["smarthome_id"] == test_credentials["smarthome_id"]

    @pytest.mark.unit
    def test_get_zones_not_authenticated(self, test_credentials):
        """Test that get_zones raises exception when not authenticated."""
        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )

        # Should raise exception when no token
        with pytest.raises(Exception, match="Not authenticated"):
            api.get_zones()

    @pytest.mark.unit
    def test_get_zones_empty_response(self, test_credentials, mock_empty_zones_response, mock_requests_session):
        """Test handling of empty zones response."""
        # Setup API client with token
        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )
        api._access_token = "mock_token"

        # Setup mock response with empty zones
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_empty_zones_response
        mock_requests_session.return_value = mock_response

        # Get zones
        zones = api.get_zones()

        # Should return empty list
        assert zones == []

    @pytest.mark.unit
    def test_get_zones_api_error(self, test_credentials, mock_requests_session):
        """Test handling of API error when getting zones."""
        # Setup API client with token
        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )
        api._access_token = "mock_token"

        # Setup mock response with error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_requests_session.return_value = mock_response

        # Get zones should return empty list on error
        zones = api.get_zones()
        assert zones == []

    @pytest.mark.unit
    def test_temperature_data_extraction(self, test_credentials, mock_zones_response):
        """Test that temperature data can be extracted from zones."""
        zones_list = mock_zones_response["data"]["zones"]

        # Living Room: 720 tenths of °F = 72.0°F = 22.2°C
        living_room = zones_list[0]
        living_room_device = living_room["devices"][0]
        temp_raw = living_room_device["temperature_air"]
        temp_f = float(temp_raw) / 10.0
        temp_c = (temp_f - 32) * 5 / 9

        assert temp_f == 72.0
        assert round(temp_c, 1) == 22.2

        # Bedroom: 680 tenths of °F = 68.0°F = 20.0°C
        bedroom = zones_list[1]
        bedroom_device = bedroom["devices"][0]
        temp_raw = bedroom_device["temperature_air"]
        temp_f = float(temp_raw) / 10.0
        temp_c = (temp_f - 32) * 5 / 9

        assert temp_f == 68.0
        assert round(temp_c, 1) == 20.0


class TestFenixV24APIIntegration:
    """Integration tests for FenixV24API using real API credentials.

    These tests require real credentials to be set in environment variables:
    - FENIX_TEST_EMAIL
    - FENIX_TEST_PASSWORD
    - FENIX_TEST_SMARTHOME_ID

    Run with: pytest tests/test_api.py -m integration
    """

    @pytest.mark.integration
    def test_real_authentication(self, test_credentials, real_api_available):
        """Test authentication with real API credentials."""
        if not real_api_available:
            pytest.skip("Real API credentials not available")

        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )

        # Should authenticate successfully
        api.authenticate()

        # Should have valid token
        assert api._access_token is not None
        assert api._refresh_token is not None
        assert api._token_expires_at > datetime.now()

    @pytest.mark.integration
    def test_real_get_zones(self, test_credentials, real_api_available):
        """Test retrieving zones with real API credentials."""
        if not real_api_available:
            pytest.skip("Real API credentials not available")

        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )

        # Authenticate and get zones (returns list of tuples)
        api.authenticate()
        zones = api.get_zones()

        # Should have at least one zone
        assert len(zones) > 0

        # Each zone should be a tuple (zone_id, zone_data)
        for zone_id, zone_data in zones:
            assert zone_id is not None
            assert "zone_label" in zone_data
            assert "devices" in zone_data

            # Print zone info for debugging
            zone_label = zone_data["zone_label"]
            print(f"\nZone: {zone_label} (ID: {zone_id})")
            devices = zone_data.get("devices", {})
            if devices:
                for device_key, device in devices.items():
                    if "temperature_air" in device:
                        temp_raw = device["temperature_air"]
                        temp_f = float(temp_raw) / 10.0
                        temp_c = (temp_f - 32) * 5 / 9
                        print(f"  Device {device_key} Temperature: {temp_c:.1f}°C ({temp_f:.1f}°F)")

    @pytest.mark.integration
    def test_real_temperature_data(self, test_credentials, real_api_available):
        """Test retrieving and parsing real temperature data."""
        if not real_api_available:
            pytest.skip("Real API credentials not available")

        api = FenixV24API(
            test_credentials["email"],
            test_credentials["password"],
            test_credentials["smarthome_id"],
        )

        # Authenticate and get zones (returns list of tuples)
        api.authenticate()
        zones = api.get_zones()

        # Find a zone with temperature data
        found_temperature = False
        for zone_id, zone_data in zones:
            devices = zone_data.get("devices", {})
            if devices:
                # Get primary device (device '0')
                primary_device = devices.get("0", {})
                temp_raw = primary_device.get("temperature_air")

                if temp_raw:
                    # Convert temperature
                    temp_f = float(temp_raw) / 10.0
                    temp_c = (temp_f - 32) * 5 / 9
                    temp_c_rounded = round(temp_c, 1)

                    # Verify temperature is in reasonable range
                    assert -50 < temp_c_rounded < 50, f"Temperature {temp_c_rounded}°C seems unreasonable"

                    found_temperature = True
                    zone_label = zone_data.get("zone_label", "Unknown")
                    print(f"\n{zone_label}: {temp_c_rounded}°C")

        # Should have found at least one temperature reading
        assert found_temperature, "No temperature data found in any zone"
