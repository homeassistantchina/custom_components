### Smart Mi fan

- Copy custom_components/fan/smart_mi_fan.py to your local HASS configuration folder.
- Install *python-miio* lib. ```pip3 install python-miio```.
- Make sure your fan is powered on and connected to the same local network with your PC.
- Get your fan's IP addr in MiJia app. Run ```miio discover``` to get fans token. 

```
INFO:miio.miio:  IP 192.168.1.154: 701 - token: b'xxxxxxxxxxxxxxxxxxxxx'
```

- Config HASS

```
fan:
  - platform: smart_mi_fan
    name: "livingroomfan"
    host: !secret fan_ip
    token: !secret fan_key
```

- Addition usage. You can create some virtual devices to control fan's speed, oscillation, natural wind mode.  
  Add this example config to your HASS configuation.yaml

```
group:
  SmartMiFan:
    entities:
      - fan.livingroomfan
      - input_slider.smart_mi_fan_speed_slider
      - input_select.smart_mi_fan_shake_head_select
      - switch.smart_mi_fan_natural_wind_switch

input_slider:
  smart_mi_fan_speed_slider:
    name: smart_mi_fan_speed_slider
    initial: 0
    min: 0
    max: 100
    step: 1

input_select:
  smart_mi_fan_shake_head_select:
    name: smart_mi_fan_shake_head_select
    options:
      - '0'
      - '30'
      - '60'
      - '90'
      - '120'
    initial: '0'

sensor:
  - platform: template
    sensors:
      current_smart_mi_fan_speed:
        value_template: '{{ states.fan.livingroomfan.attributes.speed_num }}'
      current_smart_mi_fan_shake_head_angle:
        value_template: '{{ states.fan.livingroomfan.attributes.angle }}'

switch:
  - platform: template
    switches:
      smart_mi_fan_natural_wind_switch:
        value_template: "{{ (states.fan.livingroomfan.state == 'on') and (states.fan.livingroomfan.attributes.natural_level != 0) }}"
        turn_on:
          service: fan.oscillate
          data:
            entity_id: fan.livingroomfan
            oscillating: true
        turn_off:
          service: fan.oscillate
          data:
            entity_id: fan.livingroomfan
            oscillating: false
```

  Add this automation to your HASS sutomations.yaml

```
- id: smart_mi_fan_speed_slider_control_fan
  alias: smart_mi_fan_speed_slider_control
  trigger:
  - platform: state
    entity_id: input_slider.smart_mi_fan_speed_slider
  action:
  - service: fan.set_speed
    data_template:
      entity_id: fan.livingroomfan
      speed: '{{ trigger.to_state.state | int }}'

- id: smart_mi_fan_speed_sync_with_slider
  alias: smart_mi_fan_speed_sync_with_slider
  trigger:
  - platform: state
    entity_id: sensor.current_smart_mi_fan_speed
  action:
  - service: input_slider.select_value
    data_template:
      entity_id: input_slider.smart_mi_fan_speed_slider
      value: '{{ trigger.to_state.state }}'

- id: smart_mi_fan_shake_head_select_control_fan
  alias: smart_mi_fan_shake_head_select_control_fan
  trigger:
  - platform: state
    entity_id: input_select.smart_mi_fan_shake_head_select
  action:
  - service: fan.set_direction
    data_template:
      entity_id: fan.livingroomfan
      direction: '{{ trigger.to_state.state | int }}'

- id: smart_mi_fan_shake_head_sync_with_select
  alias: smart_mi_fan_shake_head_sync_with_select
  trigger:
  - platform: state
    entity_id: sensor.current_smart_mi_fan_shake_head_angle
  action:
  - service: input_select.select_option
    data_template:
      entity_id: input_select.smart_mi_fan_shake_head_select
      option: '{{ trigger.to_state.state }}'
```