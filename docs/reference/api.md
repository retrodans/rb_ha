# Fenix V24 API Reference

Complete API reference for the Fenix V24 heating system, reverse-engineered from the homebridge project and web interface.

## Authentication

### OAuth2 Token Endpoint

**Endpoint**: `POST https://auth.aks.mutualized.wattselectronics.com/realms/fenix/protocol/openid-connect/token`

**Content-Type**: `application/x-www-form-urlencoded`

**Parameters**:

| Parameter    | Value                      |
|-------------|----------------------------|
| grant_type  | password                   |
| client_id   | app-front                  |
| username    | Your Fenix account email   |
| password    | Your Fenix account password|
| scope       | openid email profile       |

**Response**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "expires_in": 300,
  "token_type": "Bearer"
}
```

**Token lifetime**: 300 seconds (5 minutes). The integration refreshes 30 seconds before expiry.

---

## API Base URL

```
https://v24.fenixgroup.eu/api/v0.1/human
```

All requests require an `Authorization: Bearer <access_token>` header.

---

## Endpoints

### Read Smart Home Data

`POST /smarthome/read/`

Retrieves all zones and device data for a smarthome.

**Parameters**:

| Parameter     | Description              |
|--------------|--------------------------|
| smarthome_id | Your smart home ID       |
| lang         | Language code (e.g. `en_GB`) |

**Response structure**:
```json
{
  "code": {"code": "1", "key": "OK", "value": "OK"},
  "data": {
    "zones": [
      {
        "num_zone": "1",
        "zone_label": "Living Room",
        "devices": [
          {
            "id_device": "C006-005",
            "temperature_air": "689",
            "nv_mode": "11",
            "consigne_manuel": "645",
            "consigne_confort": "590",
            "consigne_eco": "554",
            "consigne_hg": "410",
            "min_set_point": "410",
            "max_set_point": "986"
          }
        ]
      }
    ]
  }
}
```

**Note**: Zones can be returned as either a list (with `num_zone` field) or a dict (with zone IDs as keys). The integration handles both formats.

---

### Set Device Mode / Temperature

`POST /query/push/`

Changes the operating mode or temperature setpoint for a device.

**Parameters**:

| Parameter              | Description                          | Required |
|-----------------------|--------------------------------------|----------|
| token                 | OAuth2 access token                  | Always   |
| smarthome_id          | Your smart home ID                   | Always   |
| context               | Always `1`                           | Always   |
| query[id_device]      | Device ID (e.g. `C006-005`)          | Always   |
| query[gv_mode]        | Target mode number                   | Always   |
| query[nv_mode]        | Target mode number (same as gv_mode) | Always   |
| query[consigne_manuel]| Manual temperature setpoint          | Mode 15  |
| query[consigne_hg]    | Antifreeze temperature setpoint      | Mode 13  |

---

## Device Parameters

Values returned by `/smarthome/read/`:

| Parameter          | Description              | Format          | Example                  |
|-------------------|--------------------------|-----------------|--------------------------|
| `id_device`       | Device identifier        | String          | `C006-005`               |
| `temperature_air` | Current air temperature  | Tenths of °F    | `689` (68.9°F = 20.5°C)  |
| `nv_mode`         | Current operating mode   | Integer         | `11` (Auto)              |
| `consigne_manuel` | Manual mode setpoint     | Tenths of °F    | `698` (69.8°F = 21.0°C)  |
| `consigne_confort`| Comfort mode setpoint    | Tenths of °F    | `590` (59.0°F = 15.0°C)  |
| `consigne_eco`    | Eco mode setpoint        | Tenths of °F    | `554` (55.4°F = 13.0°C)  |
| `consigne_hg`     | Antifreeze setpoint      | Tenths of °F    | `410` (41.0°F = 5.0°C)   |
| `min_set_point`   | Minimum allowed temp     | Tenths of °F    | `410` (41.0°F = 5.0°C)   |
| `max_set_point`   | Maximum allowed temp     | Tenths of °F    | `986` (98.6°F = 37.0°C)  |

---

## Discovering More Endpoints

To find additional API features:

1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Visit https://v24.fenixgroup.eu
4. Perform the action you want to reverse-engineer
5. Look for POST requests to `/api/v0.1/human/*`
6. Examine the request payload and response
