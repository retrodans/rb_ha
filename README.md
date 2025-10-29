# Retrobadger Home Assistant Custom Integrations

This repository contains custom Home Assistant integrations for various smart home devices.

## Fenix V24 Heating System Integration

A custom integration for the Fenix V24 heating system that provides temperature sensors for each zone in your home.

### Features

- Automatic discovery of all zones in your Fenix V24 system
- Temperature sensors for each zone
- OAuth2 authentication with automatic token refresh
- Configuration via Home Assistant UI (no YAML required)

### Installation

#### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=retrobadger&repository=rb_ha&category=integration)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Open HACS in your Home Assistant instance
3. Go to "Integrations"
4. Click the three dots (⋮) in the top right corner
5. Select "Custom repositories"
6. Add repository URL: `https://github.com/retrobadger/rb_ha`
7. Select category: "Integration"
8. Click "Add"
9. Find "Fenix V24 Heating System" in HACS and click "Download"
10. Restart Home Assistant
11. Go to **Settings** → **Devices & Services** → **Add Integration**
12. Search for "Fenix V24 Heating System" and follow the setup wizard

#### Manual Installation

1. Copy the `custom_components/fenix_v24` folder to your Home Assistant's `config/custom_components/` directory:
   ```
   config/
   └── custom_components/
       └── fenix_v24/
           ├── __init__.py
           ├── config_flow.py
           ├── manifest.json
           ├── sensor.py
           └── strings.json
   ```

2. Restart Home Assistant

3. Go to **Settings** → **Devices & Services** → **Add Integration**

4. Search for "Fenix V24 Heating System"

5. Enter your credentials:
   - Email: Your Fenix V24 account email
   - Password: Your Fenix V24 account password
   - Smarthome ID: Your smarthome ID (format: `<SMARTHOME_ID_FROM_WEBSITE_URL>`)

6. Your temperature sensors will appear automatically!

### Finding Your Smarthome ID

You can find your smarthome ID by:
1. Logging into the Fenix V24 web interface
2. Checking the URL or API calls in your browser's developer tools
3. Or contact Fenix support

### Current Features

- **Temperature Sensors**: Real-time temperature readings for each zone

### Future Features (Planned)

- Climate entity for thermostat control
- Set temperature setpoints
- Control heating modes
- Zone on/off control

### Troubleshooting

Check the Home Assistant logs for any errors:
```
Settings → System → Logs
```

Look for entries containing `fenix_v24` or `Fenix V24`
