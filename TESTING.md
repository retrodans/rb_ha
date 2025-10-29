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

### ✅ All Tests Passing (58 passed, 4 skipped)

**API Tests (9 tests)**
```
✅ test_api_initialization
✅ test_authenticate_success
✅ test_authenticate_failure
✅ test_authenticate_uses_cached_token
✅ test_get_zones_success
✅ test_get_zones_not_authenticated
✅ test_get_zones_empty_response
✅ test_get_zones_api_error
✅ test_temperature_data_extraction
```

**Integration Structure Tests (49 tests)**
```
✅ File structure validation (9 tests)
✅ manifest.json validation (13 tests)
✅ strings.json validation (5 tests)
✅ Python syntax checks (15 tests)
✅ Import structure checks (2 tests)
✅ Deployment readiness (5 tests)
```

## Test Coverage

### ✅ API Functionality Tests (test_api.py)
- **Authentication**: OAuth2 flow, token caching, error handling
- **Zone Retrieval**: API communication, data parsing, error handling
- **Temperature Data**: Fahrenheit to Celsius conversion

### ✅ Integration Structure Tests (test_integration_structure.py)
- **File Structure**: All required files exist and are readable
- **manifest.json**: Valid JSON, required keys, correct domain
- **strings.json**: Valid JSON, config flow fields, error messages
- **Python Files**: Syntax validation, docstrings, required classes
- **Imports**: No circular dependencies, standalone imports work
- **Deployment**: No test credentials, proper encoding, .gitignore

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
| File Structure | 9 tests | ✅ Passing |
| manifest.json Validation | 13 tests | ✅ Passing |
| strings.json Validation | 5 tests | ✅ Passing |
| Python Syntax & Structure | 15 tests | ✅ Passing |
| Import Structure | 2 tests | ✅ Passing |
| Deployment Readiness | 5 tests | ✅ Passing |
| **Total** | **58 tests** | **✅ All Passing** |

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
