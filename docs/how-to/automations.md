# Automation Examples

Examples of using Fenix V24 sensors in Home Assistant automations.

## Alert When Room is Off and Cold

```yaml
automation:
  - alias: "Alert: Bedroom Off and Cold"
    trigger:
      - platform: numeric_state
        entity_id: sensor.fenix_main_bedroom_temperature
        below: 16
    condition:
      - condition: state
        entity_id: sensor.fenix_main_bedroom_mode
        state: "Off"
    action:
      - service: notify.mobile_app
        data:
          message: >
            Main Bedroom is off and getting cold
            ({{ states('sensor.fenix_main_bedroom_temperature') }}°C)
```

## Notify on Mode Change

```yaml
automation:
  - alias: "Living Room Mode Changed"
    trigger:
      - platform: state
        entity_id: sensor.fenix_living_room_mode
    action:
      - service: notify.mobile_app
        data:
          message: >
            Living Room heating changed from
            {{ trigger.from_state.state }} to {{ trigger.to_state.state }}
```

## Conditional Card - Show Warning if Off

```yaml
type: conditional
conditions:
  - entity: sensor.fenix_living_room_mode
    state: "Off"
card:
  type: markdown
  content: "Living Room heating is OFF"
```

## Dashboard: Mode Status Grid

```yaml
type: grid
cards:
  - type: entity
    entity: sensor.fenix_living_room_mode
    name: Living Room
  - type: entity
    entity: sensor.fenix_kitchen_mode
    name: Kitchen
  - type: entity
    entity: sensor.fenix_main_bedroom_mode
    name: Bedroom
  - type: entity
    entity: sensor.fenix_dans_office_mode
    name: Dans Office
columns: 2
```

## Dashboard: Temperature and Mode Together

```yaml
type: entities
entities:
  - entity: sensor.fenix_living_room_temperature
  - entity: sensor.fenix_living_room_mode
  - entity: sensor.fenix_kitchen_temperature
  - entity: sensor.fenix_kitchen_mode
```
