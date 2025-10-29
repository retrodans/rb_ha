# Fenix V24 Integration Tests

This directory contains tests for the Fenix V24 Home Assistant integration.

## Test Types

### Unit Tests (Mocked)
Unit tests use mocked responses and don't make real API calls. They test individual components in isolation.

**Run unit tests:**
```bash
pytest tests/ -m unit
```

### Integration Tests (Real API)
Integration tests use real API credentials and make actual API calls to validate the integration works with the real Fenix V24 service.

**Run integration tests:**
```bash
# Set your real credentials first
export FENIX_TEST_EMAIL="your_email@example.com"
export FENIX_TEST_PASSWORD="your_password"
export FENIX_TEST_SMARTHOME_ID="your_smarthome_id"

# Run the tests
pytest tests/ -m integration
```

## Setup

### 1. Install Test Dependencies

```bash
pip install -r requirements_test.txt
```

### 2. Run Tests

**Run all tests (unit only, unless credentials are set):**
```bash
pytest
```

**Run specific test file:**
```bash
pytest tests/test_api.py
```

**Run specific test:**
```bash
pytest tests/test_api.py::TestFenixV24APIUnit::test_authenticate_success
```

**Run with verbose output:**
```bash
pytest -vv
```

**Run with coverage report:**
```bash
pytest --cov=custom_components/fenix_v24 --cov-report=html
```

## Test Structure

```
tests/
├── __init__.py              - Package marker
├── conftest.py              - Shared fixtures and configuration
├── test_api.py              - API client tests
├── test_config_flow.py      - Config flow tests
└── README.md                - This file
```

## Writing New Tests

### Unit Test Example

```python
@pytest.mark.unit
def test_my_feature(mock_requests_session):
    """Test description."""
    # Setup mock
    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests_session.return_value = mock_response

    # Test your code
    # ...

    # Assert results
    assert result == expected
```

### Integration Test Example

```python
@pytest.mark.integration
def test_real_api_call(test_credentials, real_api_available):
    """Test description."""
    if not real_api_available:
        pytest.skip("Real API credentials not available")

    # Test with real API
    # ...

    assert result is not None
```

## Continuous Integration

For CI/CD pipelines, you can run only unit tests (no credentials needed):

```bash
pytest -m unit
```

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running pytest from the repository root:

```bash
cd /path/to/rb_ha
pytest
```

### Missing Dependencies

Install all test dependencies:

```bash
pip install -r requirements_test.txt
```

### Integration Tests Failing

Ensure your credentials are correct:

```bash
# Test authentication manually
python -c "
import sys
sys.path.insert(0, 'custom_components/fenix_v24')
from api import FenixV24API
api = FenixV24API('your_email', 'your_password', 'your_smarthome_id')
api.authenticate()
print('Success!')
"
```
