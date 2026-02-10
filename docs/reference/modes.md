# Operating Modes Reference

## Mode Values

| Raw Value | Mode Name    | Description                                    | Confirmed |
|-----------|-------------|------------------------------------------------|-----------|
| 0         | Manual      | Fixed temperature, ignores schedule (forced)   | Yes       |
| 1         | Off         | Heating completely disabled                    | Yes       |
| 2         | Antifreeze  | Frost protection only (~5°C, `consigne_hg`)    | Yes       |
| 8         | Auto        | Following programmed schedule (timer)          | Yes       |
| 11        | ?           | Unknown - needs testing                        |           |
| 13        | ?           | Unknown - needs testing                        |           |
| 15        | ?           | Unknown - needs testing                        |           |

## Mode Sensor Entity Names

Each zone creates a mode sensor:

| Zone                | Entity ID                                |
|--------------------|------------------------------------------|
| Dans Office        | `sensor.fenix_dans_office_mode`          |
| Upstairs Hall      | `sensor.fenix_upstairs_hall_mode`        |
| Theas Room         | `sensor.fenix_theas_room_mode`          |
| Kitchen            | `sensor.fenix_kitchen_mode`             |
| Shivs Office       | `sensor.fenix_shivs_office_mode`        |
| Living Room        | `sensor.fenix_living_room_mode`         |
| Main Bedroom       | `sensor.fenix_main_bedroom_mode`        |
| Downstairs Hallway | `sensor.fenix_downstairs_hallway_mode`   |

## Mode Sensor Attributes

Each mode sensor exposes:

- `raw_mode` - The numeric mode value from the API (e.g. `11`)
- `device_id` - The device ID for this zone (e.g. `C006-005`)

Access in templates:
```yaml
{{ state_attr('sensor.fenix_living_room_mode', 'raw_mode') }}
{{ state_attr('sensor.fenix_living_room_mode', 'device_id') }}
```

## Temperature Conversion

The API uses tenths of degrees Fahrenheit.

### API value to Celsius

```
celsius = (api_value / 10 - 32) * 5 / 9
```

Example: `689` → 68.9°F → 20.5°C

### Celsius to API value

```
api_value = ((celsius * 9/5) + 32) * 10
```

### Common Temperature Values

| Celsius | Fahrenheit | API Value |
|---------|-----------|-----------|
| 5°C     | 41.0°F    | 410       |
| 16°C    | 60.8°F    | 608       |
| 18°C    | 64.4°F    | 644       |
| 19°C    | 66.2°F    | 662       |
| 20°C    | 68.0°F    | 680       |
| 21°C    | 69.8°F    | 698       |
| 22°C    | 71.6°F    | 716       |
| 23°C    | 73.4°F    | 734       |

## Zone Device IDs

| Zone                | Device ID  |
|--------------------|------------|
| Dans Office        | C001-000   |
| Upstairs Hall      | C002-001   |
| Theas Room         | C003-002   |
| Kitchen            | C004-003   |
| Shivs Office       | C005-004   |
| Living Room        | C006-005   |
| Main Bedroom       | C007-006   |
| Downstairs Hallway | C008-007   |
