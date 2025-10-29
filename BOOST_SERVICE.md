# Boost Service - User Guide

## Overview

The Fenix V24 integration now includes a `set_boost` service that allows you to trigger boost mode for any zone. This is perfect for automations where you want to temporarily increase heating.

## Service: `fenix_v24.set_boost`

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `entity_id` | Yes | - | The temperature sensor entity for the zone (e.g., `sensor.fenix_living_room_temperature`) |
| `duration_minutes` | No | 30 | How long to run boost mode (5-120 minutes) |

### Example Usage

#### In Automations

**Example: Boost Living Room when arriving home**

```yaml
automation:
  - alias: "Boost Living Room on Arrival"
    trigger:
      - platform: state
        entity_id: person.dan
        to: "home"
    action:
      - service: fenix_v24.set_boost
        data:
          entity_id: sensor.fenix_living_room_temperature
          duration_minutes: 60
```

**Example: Boost bedroom in the morning**

```yaml
automation:
  - alias: "Morning Bedroom Boost"
    trigger:
      - platform: time
        at: "06:30:00"
    action:
      - service: fenix_v24.set_boost
        data:
          entity_id: sensor.fenix_main_bedroom_temperature
          duration_minutes: 30
```

**Example: Boost multiple zones**

```yaml
automation:
  - alias: "Boost Downstairs Zones"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      - service: fenix_v24.set_boost
        data:
          entity_id: sensor.fenix_living_room_temperature
          duration_minutes: 45
      - service: fenix_v24.set_boost
        data:
          entity_id: sensor.fenix_kitchen_temperature
          duration_minutes: 45
```

#### In Scripts

```yaml
script:
  boost_living_room:
    alias: "Boost Living Room"
    sequence:
      - service: fenix_v24.set_boost
        data:
          entity_id: sensor.fenix_living_room_temperature
          duration_minutes: 30
```

#### From Developer Tools

1. Go to **Developer Tools → Services**
2. Select service: `fenix_v24.set_boost`
3. Fill in the YAML:

```yaml
entity_id: sensor.fenix_living_room_temperature
duration_minutes: 30
```

4. Click **Call Service**

## What Boost Mode Does

When you call the boost service:

1. The zone switches to **mode 16** (boost mode)
2. The temperature setpoint is set to the **boost temperature** (configured in your Fenix app)
3. The boost timer is set to your specified duration
4. After the duration expires, the zone returns to its previous mode (typically Auto/schedule)

## Your Available Zones

Based on your system, here are the entity IDs you can use:

- `sensor.fenix_dans_office_temperature` - Dans Office
- `sensor.fenix_upstairs_hall_temperature` - UPSTAIRS HALL
- `sensor.fenix_theas_room_temperature` - Theas Room
- `sensor.fenix_kitchen_temperature` - Kitchen
- `sensor.fenix_shivs_office_temperature` - Shivs Office
- `sensor.fenix_living_room_temperature` - Living Room
- `sensor.fenix_main_bedroom_temperature` - Main Bedroom
- `sensor.fenix_downstairs_hallway_temperature` - Downstairs Hallway

## Testing the Boost Service

### Important: Test Carefully!

Before using in automations, test manually first:

1. **Go to Developer Tools → Services**
2. **Call the service** for one zone with a short duration:
   ```yaml
   entity_id: sensor.fenix_dans_office_temperature
   duration_minutes: 5
   ```
3. **Check the Fenix app** - verify boost mode is active
4. **Wait 5 minutes** - verify it returns to normal mode
5. **Check Home Assistant logs** for any errors

### Checking Logs

After calling the service, check logs:

**Settings → System → Logs**

Search for: `boost`

You should see:
```
INFO [custom_components.fenix_v24] Triggering boost for sensor.fenix_living_room_temperature (device C006-005) for 30 minutes
INFO [custom_components.fenix_v24.api] Setting boost mode for device C006-005 for 30 minutes
INFO [custom_components.fenix_v24.api] Successfully enabled boost for device C006-005
INFO [custom_components.fenix_v24] Boost enabled successfully for sensor.fenix_living_room_temperature
```

## Troubleshooting

### Error: "Entity does not support boost mode"

**Cause:** The entity_id doesn't belong to a Fenix V24 temperature sensor.

**Fix:** Make sure you're using the correct entity_id from the list above.

### Error: "Failed to set boost"

**Cause:** The API request failed. Could be authentication, network, or API issue.

**Fix:**
1. Check Home Assistant logs for details
2. Verify the integration is working (sensors show temperatures)
3. Try restarting the integration

### Boost doesn't start

**Cause:** The boost mode value might be different than expected.

**Fix:**
1. Check the Fenix V24 web interface while manually enabling boost
2. Open browser developer tools (F12) → Network tab
3. Look for the `/query/push/` request
4. Check what parameters are sent (especially the mode value)
5. Report back the findings so we can update the code

## Notes

- The boost implementation is based on analysis of the API data structure
- Mode 16 was observed in your zone data, suggesting it's boost mode
- If boost doesn't work as expected, we can adjust the mode value or parameters
- You can only boost one zone at a time per service call (but you can call it multiple times)

## Files Modified

If you're deploying manually, these files need updating:

1. `custom_components/fenix_v24/__init__.py` - Service registration
2. `custom_components/fenix_v24/api.py` - Boost API method
3. `custom_components/fenix_v24/sensor.py` - Pass device_id to entities
4. `custom_components/fenix_v24/temperature_sensor.py` - Store device_id
5. `custom_components/fenix_v24/services.yaml` - Service definition

## Deployment

After copying the updated files:

1. **Restart Home Assistant**
2. The service will be available immediately
3. No need to remove/re-add the integration

## Example Integration with Your Messaging

Since you mentioned you have automations sending messages, you can combine them:

```yaml
automation:
  - alias: "Cold Weather Alert with Boost"
    trigger:
      - platform: numeric_state
        entity_id: sensor.fenix_living_room_temperature
        below: 18
    action:
      - service: notify.mobile_app
        data:
          message: "Living room is cold ({{ states('sensor.fenix_living_room_temperature') }}°C). Boosting heat!"
      - service: fenix_v24.set_boost
        data:
          entity_id: sensor.fenix_living_room_temperature
          duration_minutes: 60
```

Enjoy your new boost functionality!
