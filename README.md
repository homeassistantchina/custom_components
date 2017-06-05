# Non official Home Assistant Components

## Description

Those non-official components are maintained by [Hassbian](https://bbs.hassbian.com/forum.php)

## Components list

- Smart Mi fan
- Chuamg Mi IR remote

## Installation

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

### Chuang Mi IR remote
- Copy custom_components/switch/chuangmi_ir.py to your local HASS configuration folder.
- We *CAN NOT* got chuangmi ir remote token by miio discover command. It will return all zero.

```
INFO:miio.miio:  IP 192.168.1.191: 174 - token: b'00000000000000000000000000000000'
```

- We can get token adb connect to an *ROOT* Android phone. Install MiJia app. Login your account and control IR remote by using this app
- Connect your phone to PC, and run

```
adb root
adb shell
cd /data/data/com.xiaomi.smarthome/cache/smrc4-cache
grep -nr token .
```

- You will find there are lots of files contains device token. You can copy one of it and format it do human readable json format.

```
{
    "did": "123456",
    "token": "asdfghjhjkl",
    "longitude": 111111,
    "latitude": 22222,
    "name": "客厅的万能遥控器",
    "pid": "0",
    "localip": "192.168.1.191",
    "mac": "xxxxxxxxxxx",
    "ssid": "SchumyOpenWrt",
    "bssid": "20:76:93:3D:3B:24",
    "parent_id": "",
    "parent_model": "",
    "extra": {
	    "isSetPincode": 0,
        "fw_version": "1.2.4_38",
        "needVerifyCode": 0,
        "isPasswordEncrypt": 0
    },
    "show_mode": 1,
    "model": "chuangmi.ir.v2",
    "adminFlag": 1,
    "shareFlag": 0,
    "permitLevel": 16,
	"rssi": -51,
    "isOnline": true,
    "desc": "Added 5 remotes "
}
```

- Config HASS

```
switch:
  - platform: chuangmi_ir
    name: "livingroomirremote"
    host: !secret chuangmi_ip
    token: !secret chuangmi_key
    switches:
      reciever:
        command_on: ''
        command_off: ''
```

- To learn IR command, you can call service. Service Domain is chuangmi, service is learn_command_YOUR_DEVICE_IP.
- After call this service, using the real IR remote send one key to Chuangmi IR remote.
- You will get a notification in your HASS States page. Contains learnt IR command. Such as *Z6VLAAkCAABpAgAAYgYAAKYIAACJEQAAoSMAAKScAABYeQEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFAQEBAQEBAQEhISEhISEhIQEBISEBAQEBISEBASEhISFhNXE1AQ==*
- Copy the learnt command to command_on or command_off. This is an example

```
- platform: chuangmi_ir
  host: !secret chuangmi_ip
  name: "livingroomirremote"
  token: !secret chuangmi_key
  switches:
    reciever:
      command_on: ''
      command_off: ''
    wcfan:
      name: 'wcfan'
      command_on: 'Z6VLAAkCAABpAgAAYgYAAKYIAACJEQAAoSMAAKScAABYeQEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFAQEBAQEBAQEhISEhISEhIQEBISEBAQEBISEBASEhISFhNXE1AQ=='
      command_off: 'Z6VHAPEBAACBAgAASQYAAIYIAABqEQAAySMAAECcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABFAQEBAQEBAQEhISEhISEhIQEBASEhAQEBISEhAQEhISFhNQE='
```
- You may learnt some IR command before in MiJia App. The command can be got in /data/data/com.xiaomi.smarthome/files/IR_REMOTE_DID_device.json