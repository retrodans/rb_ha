# Fenix V24 Heating System - Home Assistant Integration

A custom Home Assistant integration for the Fenix V24 heating system. Provides temperature and mode sensors for each heating zone.

## Features

- Automatic discovery of all heating zones
- Temperature sensors for each zone (real-time, polled every ~30s)
- Mode sensors showing current operating mode (Auto, Manual, Eco, Off, Antifreeze)
- OAuth2 authentication with automatic token refresh
- Configuration via Home Assistant UI (no YAML required)

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=retrobadger&repository=rb_ha&category=integration)

1. Ensure [HACS](https://hacs.xyz/) is installed
2. Open HACS, click the three dots, select "Custom repositories"
3. Add repository URL: `https://github.com/retrodans/rb_ha`, type: "Integration"
4. Find "Fenix V24 Heating System" and click "Download"
5. Restart Home Assistant
6. Go to **Settings > Devices & Services > Add Integration** and search for "Fenix V24"

### Manual Installation

1. Copy `custom_components/fenix_v24/` to your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings > Devices & Services > Add Integration** and search for "Fenix V24"

### Deploying via SSH

Use the included deploy script:
```bash
HA_HOST=homeassistant.local ./deploy_to_ha.sh
```

## Setup

You'll need:
- **Email**: Your Fenix V24 account email
- **Password**: Your Fenix V24 account password
- **Smarthome ID**: Found in the URL when logged into the Fenix V24 web interface

## Documentation

Docs follow the [Diataxis](https://diataxis.fr/) model:

- [API Reference](docs/reference/api.md) - Endpoints, parameters, response formats
- [Modes Reference](docs/reference/modes.md) - Mode values, device IDs, temperature conversion
- [Automation Examples](docs/how-to/automations.md) - HA automations and dashboard cards
- [Architecture](docs/explanation/architecture.md) - How the integration works

## API Testing with Bruno

A [Bruno](https://www.usebruno.com/) collection is included in `.bruno/` for testing the Fenix API directly. Configure your credentials in `.bruno/environments/fenix.bru`, then use the requests to experiment with mode changes before integrating them into HA.

## Troubleshooting

Check Home Assistant logs for entries containing `fenix_v24`:

**Settings > System > Logs**
