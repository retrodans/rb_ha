"""Constants for the Fenix V24 integration."""

# Integration domain
DOMAIN = "fenix_v24"

# Fenix V24 API Configuration
# The Fenix V24 system uses Keycloak for OAuth2 authentication
KEYCLOAK_BASE = "https://auth.aks.mutualized.wattselectronics.com"
REALM = "fenix"
TOKEN_ENDPOINT = f"{KEYCLOAK_BASE}/realms/{REALM}/protocol/openid-connect/token"
API_BASE = "https://v24.fenixgroup.eu/api/v0.1/human"

# OAuth2 Configuration
CLIENT_ID = "app-front"
OAUTH_GRANT_TYPE = "password"
OAUTH_SCOPE = "openid email profile"

# API Configuration
API_TIMEOUT = 10  # seconds
TOKEN_REFRESH_MARGIN = 30  # seconds before expiry to refresh token
API_LANGUAGE = "en_GB"

# Temperature conversion
# The Fenix V24 API returns temperature in tenths of degrees Fahrenheit
TEMP_DIVISOR = 10.0
