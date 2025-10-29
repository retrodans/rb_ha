"""Tests for Fenix V24 integration file structure and validity.

This module validates that all required files exist, are valid, and have correct structure.
These tests catch common issues that cause "Config flow could not be loaded" errors.

Run tests:
    pytest tests/test_integration_structure.py -v
"""
import json
import os
import pytest
from pathlib import Path


# Path to the integration
INTEGRATION_PATH = Path(__file__).parent.parent / "custom_components" / "fenix_v24"


class TestIntegrationStructure:
    """Tests for integration file structure."""

    @pytest.mark.unit
    def test_integration_directory_exists(self):
        """Test that the integration directory exists."""
        assert INTEGRATION_PATH.exists(), f"Integration directory not found: {INTEGRATION_PATH}"
        assert INTEGRATION_PATH.is_dir(), f"Integration path is not a directory: {INTEGRATION_PATH}"

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", [
        "__init__.py",
        "manifest.json",
        "config_flow.py",
        "strings.json",
        "const.py",
        "api.py",
        "sensor.py",
        "temperature_sensor.py",
    ])
    def test_required_file_exists(self, filename):
        """Test that all required files exist."""
        filepath = INTEGRATION_PATH / filename
        assert filepath.exists(), f"Required file missing: {filename}"
        assert filepath.is_file(), f"Path exists but is not a file: {filename}"
        assert os.access(filepath, os.R_OK), f"File is not readable: {filename}"


class TestManifestJson:
    """Tests for manifest.json validity and contents."""

    @pytest.fixture
    def manifest(self):
        """Load manifest.json."""
        manifest_path = INTEGRATION_PATH / "manifest.json"
        with open(manifest_path, 'r') as f:
            return json.load(f)

    @pytest.mark.unit
    def test_manifest_json_valid(self):
        """Test that manifest.json is valid JSON."""
        manifest_path = INTEGRATION_PATH / "manifest.json"
        try:
            with open(manifest_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"manifest.json is not valid JSON: {e}")

    @pytest.mark.unit
    @pytest.mark.parametrize("required_key", [
        "domain",
        "name",
        "config_flow",
        "version",
        "codeowners",
        "documentation",
        "integration_type",
        "iot_class",
        "requirements",
    ])
    def test_manifest_has_required_key(self, manifest, required_key):
        """Test that manifest.json has all required keys."""
        assert required_key in manifest, f"manifest.json missing required key: {required_key}"

    @pytest.mark.unit
    def test_manifest_domain(self, manifest):
        """Test that manifest.json has correct domain."""
        assert manifest["domain"] == "fenix_v24", \
            f"manifest.json domain should be 'fenix_v24', got: {manifest.get('domain')}"

    @pytest.mark.unit
    def test_manifest_config_flow_enabled(self, manifest):
        """Test that config_flow is enabled in manifest.json."""
        assert manifest.get("config_flow") is True, \
            "manifest.json must have 'config_flow': true for UI configuration"

    @pytest.mark.unit
    def test_manifest_version_format(self, manifest):
        """Test that version follows semantic versioning."""
        version = manifest.get("version", "")
        parts = version.split(".")
        assert len(parts) >= 2, f"Version should be in format X.Y or X.Y.Z, got: {version}"
        for part in parts:
            assert part.isdigit(), f"Version parts should be numeric, got: {version}"

    @pytest.mark.unit
    def test_manifest_requirements(self, manifest):
        """Test that requirements are specified."""
        requirements = manifest.get("requirements", [])
        assert isinstance(requirements, list), "requirements should be a list"
        assert "requests" in " ".join(requirements), "requests library should be in requirements"


class TestStringsJson:
    """Tests for strings.json validity and structure."""

    @pytest.fixture
    def strings(self):
        """Load strings.json."""
        strings_path = INTEGRATION_PATH / "strings.json"
        with open(strings_path, 'r') as f:
            return json.load(f)

    @pytest.mark.unit
    def test_strings_json_valid(self):
        """Test that strings.json is valid JSON."""
        strings_path = INTEGRATION_PATH / "strings.json"
        try:
            with open(strings_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"strings.json is not valid JSON: {e}")

    @pytest.mark.unit
    def test_strings_has_config_section(self, strings):
        """Test that strings.json has config section."""
        assert "config" in strings, "strings.json must have 'config' section"

    @pytest.mark.unit
    def test_strings_has_user_step(self, strings):
        """Test that strings.json has user step configuration."""
        assert "config" in strings, "Missing 'config' section"
        assert "step" in strings["config"], "Missing 'step' section in config"
        assert "user" in strings["config"]["step"], "Missing 'user' step in config"

    @pytest.mark.unit
    def test_strings_has_error_messages(self, strings):
        """Test that strings.json has error messages defined."""
        assert "config" in strings, "Missing 'config' section"
        assert "error" in strings["config"], "Missing 'error' section"

        errors = strings["config"]["error"]
        required_errors = ["cannot_connect", "invalid_auth", "unknown"]
        for error_key in required_errors:
            assert error_key in errors, f"Missing error message for: {error_key}"

    @pytest.mark.unit
    def test_strings_user_data_fields(self, strings):
        """Test that all required form fields are defined."""
        data = strings["config"]["step"]["user"].get("data", {})
        required_fields = ["email", "password", "smarthome_id"]
        for field in required_fields:
            assert field in data, f"Missing form field in strings.json: {field}"


class TestPythonFiles:
    """Tests for Python file syntax and structure."""

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", [
        "__init__.py",
        "config_flow.py",
        "const.py",
        "api.py",
        "sensor.py",
        "temperature_sensor.py",
    ])
    def test_python_file_syntax(self, filename):
        """Test that Python files have valid syntax."""
        filepath = INTEGRATION_PATH / filename
        with open(filepath, 'r') as f:
            code = f.read()

        try:
            compile(code, str(filepath), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {filename}: {e}")

    @pytest.mark.unit
    @pytest.mark.parametrize("filename", [
        "__init__.py",
        "config_flow.py",
        "const.py",
        "api.py",
        "sensor.py",
        "temperature_sensor.py",
    ])
    def test_python_file_has_docstring(self, filename):
        """Test that Python files have module-level docstrings."""
        filepath = INTEGRATION_PATH / filename
        with open(filepath, 'r') as f:
            lines = f.readlines()

        # Skip empty lines and comments at start
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                assert stripped.startswith('"""') or stripped.startswith("'''"), \
                    f"{filename} should start with a docstring"
                break

    @pytest.mark.unit
    def test_init_has_domain_constant(self):
        """Test that __init__.py defines DOMAIN constant."""
        init_path = INTEGRATION_PATH / "__init__.py"
        with open(init_path, 'r') as f:
            content = f.read()

        assert 'DOMAIN = "fenix_v24"' in content, \
            "__init__.py must define DOMAIN constant"

    @pytest.mark.unit
    def test_const_has_required_constants(self):
        """Test that const.py defines all required constants."""
        const_path = INTEGRATION_PATH / "const.py"
        with open(const_path, 'r') as f:
            content = f.read()

        required_constants = [
            "DOMAIN",
            "TOKEN_ENDPOINT",
            "API_BASE",
            "CLIENT_ID",
            "API_TIMEOUT",
        ]

        for constant in required_constants:
            assert constant in content, f"const.py missing required constant: {constant}"

    @pytest.mark.unit
    def test_config_flow_has_configflow_class(self):
        """Test that config_flow.py defines ConfigFlow class."""
        config_flow_path = INTEGRATION_PATH / "config_flow.py"
        with open(config_flow_path, 'r') as f:
            content = f.read()

        assert "class ConfigFlow" in content, \
            "config_flow.py must define ConfigFlow class"
        assert "config_entries.ConfigFlow" in content, \
            "ConfigFlow must inherit from config_entries.ConfigFlow"

    @pytest.mark.unit
    def test_api_has_fenixv24api_class(self):
        """Test that api.py defines FenixV24API class."""
        api_path = INTEGRATION_PATH / "api.py"
        with open(api_path, 'r') as f:
            content = f.read()

        assert "class FenixV24API" in content, \
            "api.py must define FenixV24API class"
        assert "def authenticate" in content, \
            "FenixV24API must have authenticate method"
        assert "def get_zones" in content, \
            "FenixV24API must have get_zones method"


class TestImportStructure:
    """Tests for import dependencies and structure."""

    @pytest.mark.unit
    def test_no_circular_imports(self):
        """Test that there are no circular import dependencies."""
        # This test will fail if there are circular imports during compilation
        import sys
        sys.path.insert(0, str(INTEGRATION_PATH.parent))

        try:
            # Try importing each module - will fail if circular imports exist
            import fenix_v24.const
            import fenix_v24.api
            # Note: Can't import config_flow or sensor without Home Assistant
        except ImportError as e:
            if "homeassistant" not in str(e):
                pytest.fail(f"Import error (possible circular import): {e}")

    @pytest.mark.unit
    def test_const_imports_correctly(self):
        """Test that const.py can be imported standalone."""
        import sys
        standalone_path = str(INTEGRATION_PATH.parent / "fenix_v24_standalone")

        if os.path.exists(standalone_path):
            sys.path.insert(0, standalone_path)
            try:
                import const
                assert hasattr(const, "DOMAIN")
                assert hasattr(const, "TOKEN_ENDPOINT")
            except ImportError as e:
                pytest.fail(f"Failed to import const.py: {e}")
        else:
            pytest.skip("Standalone test files not available")


class TestDeploymentReadiness:
    """Tests to verify integration is ready for deployment."""

    @pytest.mark.unit
    def test_no_pycache_in_git(self):
        """Test that __pycache__ directories shouldn't be committed."""
        pycache_path = INTEGRATION_PATH / "__pycache__"
        gitignore_path = INTEGRATION_PATH.parent.parent / ".gitignore"

        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore = f.read()
            # Warn if pycache exists and not in gitignore
            if pycache_path.exists() and "__pycache__" not in gitignore:
                pytest.fail("__pycache__ exists but not in .gitignore")

    @pytest.mark.unit
    def test_no_test_credentials_in_code(self):
        """Test that no test credentials are hardcoded in source files."""
        dangerous_patterns = [
            "test@example.com",
            "password123",
            "TEST_PASSWORD",
        ]

        for py_file in INTEGRATION_PATH.glob("*.py"):
            if py_file.name.startswith("test_"):
                continue  # Skip test files

            with open(py_file, 'r') as f:
                content = f.read()

            for pattern in dangerous_patterns:
                assert pattern not in content, \
                    f"Found test credential pattern '{pattern}' in {py_file.name}"

    @pytest.mark.unit
    def test_all_files_have_proper_encoding(self):
        """Test that all Python files use UTF-8 encoding."""
        for py_file in INTEGRATION_PATH.glob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError:
                pytest.fail(f"{py_file.name} is not valid UTF-8")
