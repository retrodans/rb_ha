# Fenix V24 Heating System Integration

Integrate your Fenix V24 heating system with Home Assistant to monitor and control your home heating.

## Features

- **Automatic Zone Discovery**: All zones in your Fenix V24 system are automatically discovered
- **Temperature Sensors**: Real-time temperature readings for each zone
- **OAuth2 Authentication**: Secure authentication with automatic token refresh
- **UI Configuration**: Easy setup through Home Assistant's UI - no YAML editing required

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/retrobadger/rb_ha`
6. Select category: "Integration"
7. Click "Add"
8. Find "Fenix V24 Heating System" in HACS and click "Download"
9. Restart Home Assistant
10. Go to Settings → Devices & Services → Add Integration
11. Search for "Fenix V24" and follow the setup wizard

### Manual Installation

See the [README](https://github.com/retrobadger/rb_ha#installation) for manual installation instructions.

## Configuration

After installation, add the integration via the UI:

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Fenix V24 Heating System**
4. Enter your credentials:
   - **Email**: Your Fenix V24 account email
   - **Password**: Your Fenix V24 account password
   - **Smarthome ID**: Your smarthome ID (e.g., `<SMARTHOME_ID_FROM_WEBSITE_URL>`)

### Finding Your Smarthome ID

Your smarthome ID can be found by:
- Logging into the Fenix V24 web interface
- Checking the URL or network requests in your browser's developer tools
- Contacting Fenix support

## Supported Entities

### Sensors

Each zone in your Fenix V24 system will create a temperature sensor:
- Entity ID: `sensor.fenix_{zone_name}_temperature`
- Device Class: Temperature
- Unit: °C (Celsius)
- Update Interval: 30 seconds (default Home Assistant polling)

## Troubleshooting

### Authentication Errors

If you receive authentication errors:
- Verify your email and password are correct
- Ensure you can log in to the Fenix V24 web interface with the same credentials
- Check that your account is active

### Cannot Connect Errors

If you cannot connect to the API:
- Verify your smarthome ID is correct
- Check your internet connection
- Verify the Fenix V24 API is accessible

### Logs

Check Home Assistant logs for detailed error messages:
- Go to **Settings** → **System** → **Logs**
- Search for entries containing `fenix_v24`

## Future Features

Planned features for future releases:
- Climate entity for full thermostat control
- Set temperature setpoints
- Control heating modes (auto, manual, etc.)
- Zone on/off control
- Schedule management
- Energy consumption tracking (if supported by API)

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/retrobadger/rb_ha/issues).

## Credits

Developed by [@retrobadger](https://github.com/retrobadger)
