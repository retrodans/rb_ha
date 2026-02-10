# Architecture

## Overview

The Fenix V24 integration is a cloud-polling Home Assistant custom component. It authenticates against a Keycloak OAuth2 server, then polls the Fenix cloud API every ~30 seconds to read zone data.

## Components

```
custom_components/fenix_v24/
├── __init__.py              # Entry point, service registration
├── api.py                   # API client (auth, zone reading)
├── config_flow.py           # HA setup wizard UI
├── const.py                 # URLs, credentials, constants
├── manifest.json            # Integration metadata
├── mode_sensor.py           # Mode sensor entity
├── sensor.py                # Sensor platform setup
├── services.yaml            # Service definitions
├── strings.json             # UI strings
└── temperature_sensor.py    # Temperature sensor entity
```

### api.py - FenixV24API

The core API client. Handles:
- OAuth2 password grant authentication
- Token caching with automatic refresh (30s before expiry)
- Zone data retrieval (handles both list and dict response formats)
- Mode/temperature setting via `query/push`

Each config entry gets its own `FenixV24API` instance, so multiple Fenix accounts are supported.

### sensor.py

The sensor platform setup. Called by HA when the integration loads. Creates two sensors per zone:
1. **Temperature sensor** - current room temperature in Celsius
2. **Mode sensor** - current operating mode (Auto, Manual, Eco, Off, Antifreeze)

### temperature_sensor.py

Polls the API and converts the temperature value from Fahrenheit tenths to Celsius. The API returns values like `689` meaning 68.9°F, which converts to 20.5°C.

### mode_sensor.py

Polls the API and converts numeric mode codes (0, 2, 8, 11, 13, 15) to human-readable names. Exposes `raw_mode` and `device_id` as state attributes.

### config_flow.py

Implements the HA configuration UI. Validates credentials by attempting authentication and zone retrieval. Uses email as unique ID to prevent duplicate entries.

## Data Flow

```
Fenix Cloud API
      │
      ▼
  FenixV24API (api.py)
   ┌──┴──┐
   │     │
   ▼     ▼
 Temp   Mode
Sensor  Sensor
   │     │
   ▼     ▼
Home Assistant
  Entity Registry
```

## API Quirks

- **Temperature format**: Tenths of degrees Fahrenheit (not Celsius, not whole degrees)
- **Zone format**: The API sometimes returns zones as a list (with `num_zone` field) and sometimes as a dict (zone IDs as keys). The code handles both.
- **Token lifetime**: Only 5 minutes. Must refresh frequently.
- **Content-Type**: All requests use `application/x-www-form-urlencoded`, not JSON
- **Dual token passing**: The `/query/push/` endpoint requires the token both as a Bearer header AND in the form body
