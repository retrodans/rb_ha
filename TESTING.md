# Testing Guide for Fenix V24 Integration

## Quick Start

### Setup Virtual Environment

```bash
# Create virtual environment (one time)
~/.pyenv/versions/3.11.9/bin/python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements_test.txt
```

### Run Tests

```bash
# Activate venv first
source venv/bin/activate

# Run all unit tests
pytest tests/test_api.py -m unit -v

# Run specific test
pytest tests/test_api.py::TestFenixV24APIUnit::test_authenticate_success -v

# Run with less verbose output
pytest tests/ -m unit
```

## Test Results Summary

### ✅ All Unit Tests Passing (9/9)

```
tests/test_api.py::TestFenixV24APIUnit::test_api_initialization PASSED
tests/test_api.py::TestFenixV24APIUnit::test_authenticate_success PASSED
tests/test_api.py::TestFenixV24APIUnit::test_authenticate_failure PASSED
tests/test_api.py::TestFenixV24APIUnit::test_authenticate_uses_cached_token PASSED
tests/test_api.py::TestFenixV24APIUnit::test_get_zones_success PASSED
tests/test_api.py::TestFenixV24APIUnit::test_get_zones_not_authenticated PASSED
tests/test_api.py::TestFenixV24APIUnit::test_get_zones_empty_response PASSED
tests/test_api.py::TestFenixV24APIUnit::test_get_zones_api_error PASSED
tests/test_api.py::TestFenixV24APIUnit::test_temperature_data_extraction PASSED
```

## Test Coverage

### ✅ Authentication Tests
- **test_api_initialization**: Verifies API client initializes correctly
- **test_authenticate_success**: Tests successful OAuth2 authentication
- **test_authenticate_failure**: Tests handling of invalid credentials
- **test_authenticate_uses_cached_token**: Verifies token caching works

### ✅ Zone Retrieval Tests
- **test_get_zones_success**: Tests successful zone data retrieval
- **test_get_zones_not_authenticated**: Tests error when not authenticated
- **test_get_zones_empty_response**: Tests handling of empty zone list
- **test_get_zones_api_error**: Tests handling of API errors

### ✅ Temperature Data Tests
- **test_temperature_data_extraction**: Tests Fahrenheit to Celsius conversion

## Integration Tests (Optional)

To run tests against the real Fenix V24 API:

```bash
# Set your real credentials
export FENIX_TEST_EMAIL="your_email@example.com"
export FENIX_TEST_PASSWORD="your_password"
export FENIX_TEST_SMARTHOME_ID="your_smarthome_id"

# Run integration tests
pytest tests/test_api.py -m integration -v
```

### Integration Test Coverage
- **test_real_authentication**: Test real API authentication
- **test_real_get_zones**: Test retrieving real zones
- **test_real_temperature_data**: Test parsing real temperature data

## Test Commands Reference

```bash
# Run all unit tests
pytest tests/ -m unit

# Run all tests (unit + integration if credentials available)
pytest tests/

# Run with coverage report
pytest tests/ -m unit --cov=custom_components/fenix_v24_standalone --cov-report=html

# Run specific test class
pytest tests/test_api.py::TestFenixV24APIUnit

# Run tests matching pattern
pytest tests/ -k "authenticate"

# Run with detailed output
pytest tests/ -vv -s

# List all tests without running
pytest tests/ --collect-only
```

## Troubleshooting

### Import Errors
If you see import errors, make sure you're in the repository root and venv is activated:
```bash
cd /path/to/rb_ha
source venv/bin/activate
pytest tests/
```

### Module Not Found
Ensure all dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements_test.txt
```

## Test Structure

```
tests/
├── __init__.py              - Package marker
├── conftest.py              - Shared fixtures and test data
├── test_api.py              - API client tests (✅ 9 passing)
├── test_config_flow.py      - Config flow tests
└── README.md                - Detailed test documentation
```

## What's Tested

| Component | Tests | Status |
|-----------|-------|--------|
| API Authentication | 4 tests | ✅ Passing |
| Zone Retrieval | 4 tests | ✅ Passing |
| Temperature Conversion | 1 test | ✅ Passing |
| **Total** | **9 tests** | **✅ All Passing** |

## CI/CD Integration

For continuous integration pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements_test.txt
    pytest tests/ -m unit -v
```
