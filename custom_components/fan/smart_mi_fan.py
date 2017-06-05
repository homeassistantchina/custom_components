"""
Support SmartMi fan.

Thank rytilahti for his great work
https://home-assistant.io/components/demo/
"""
import logging
import random

from homeassistant.components.fan import (SPEED_OFF, FanEntity, SUPPORT_SET_SPEED,
                                          SUPPORT_OSCILLATE, SUPPORT_DIRECTION,
                                          ATTR_SPEED, ATTR_SPEED_LIST, ATTR_OSCILLATING, ATTR_DIRECTION)
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_TOKEN

REQUIREMENTS = ['python-miio==0.0.8']

_LOGGER = logging.getLogger(__name__)

FAN_ENTITY_ID = 'fan.smart_mi_fan'
FAN_DEFAULT_NAME = 'smart_mi_fan'

SMART_MI_FAN_SUPPORT = SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION

SPEED_LEVEL_1 = 'Level1'
SPEED_LEVEL_2 = 'Level2'
SPEED_LEVEL_3 = 'Level3'
SPEED_LEVEL_4 = 'Level4'
FAN_DIRECT_SPEED = {
    SPEED_OFF: range(0, 1),
    SPEED_LEVEL_1: range(1, 28),
    SPEED_LEVEL_2: range(28, 56),
    SPEED_LEVEL_3: range(56, 82),
    SPEED_LEVEL_4: range(82, 101)
}  # type: dict
FAN_NATURAL_SPEED = {
    SPEED_OFF: range(0, 1),
    SPEED_LEVEL_1: range(1, 29),
    SPEED_LEVEL_2: range(29, 55),
    SPEED_LEVEL_3: range(55, 81),
    SPEED_LEVEL_4: range(81, 100)
}  # type: dict
FAN_SPEED = [SPEED_LEVEL_1, SPEED_LEVEL_2, SPEED_LEVEL_3, SPEED_LEVEL_4]

FAN_PROP_TO_ATTR = {
    'speed': ATTR_SPEED,
    'speed_list': ATTR_SPEED_LIST,
    'speed_num': 'speed_num',
    'oscillating': ATTR_OSCILLATING,
    'direction': ATTR_DIRECTION,
    'fan_temp_dec': 'temprature',
    'fan_humidity': 'humidity',
    'fan_angle': 'angle',
    'fan_speed': 'fan_speed',
    'fan_poweroff_time': 'poweroff_time',
    'fan_power': 'power',
    'fan_ac_power': 'ac_power',
    'fan_battery': 'battery',
    'fan_angle_enable': 'angle_enable',
    'fan_speed_level': 'speed_level',
    'fan_natural_level': 'natural_level',
    'fan_child_lock': 'child_lock',
    'fan_buzzer': 'buzzer',
    'fan_led_b': 'led',
}  # type: dict

#REQUIREMENTS = ['https://github.com/SchumyHao/python-mirobo/archive/master.zip'
#                '#python-mirobo']
# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the smart mi fan platform."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME) or FAN_DEFAULT_NAME
    token = config.get(CONF_TOKEN)

    add_devices_callback([
        SmartMiFan(hass, name, host, token),
    ])

class FanStatus:
    """Container for status reports from the fan."""
    def __init__(self, data):
        #['temp_dec', 'humidity', 'angle', 'speed', 'poweroff_time', 'power', 'ac_power', 'battery', 'angle_enable', 'speed_level', 'natural_level', 'child_lock', 'buzzer', 'led_b']
        #[232, 46, 30, 298, 0, 'on', 'off', 98, 'off', 1, 0, 'off', 'on', 1]
        self.data = data

    @property
    def temp_dec(self):
        return self.data[0]
    @property
    def humidity(self):
        return self.data[1]
    @property
    def angle(self):
        return self.data[2]
    @property
    def speed(self):
        return self.data[3]
    @property
    def poweroff_time(self):
        return self.data[4]
    @property
    def power(self):
        return self.data[5]
    @property
    def ac_power(self):
        return self.data[6]
    @property
    def battery(self):
        return self.data[7]
    @property
    def angle_enable(self):
        return self.data[8]
    @property
    def speed_level(self):
        return self.data[9]
    @property
    def natural_level(self):
        return self.data[10]
    @property
    def child_lock(self):
        return self.data[11]
    @property
    def buzzer(self):
        return self.data[12]
    @property
    def led_b(self):
        return self.data[13]

class SmartMiFan(FanEntity):
    """A smart mi fan component."""

    def __init__(self, hass, name: str, host, token) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._name = name
        self._speed = None
        self._is_on = False
        self._state = None
        self._state_attrs = {}
        self.oscillating = False
        self.direction = 'forward'
        self.host = host
        self.token = token
        self._fan = None
        self._state_attrs = self.fan_get_prop()
        self._is_on = (getattr(self, 'fan_power') == 'on')
        self.oscillating = (getattr(self, 'fan_natural_level') != 0)

    @property
    def name(self) -> str:
        """Get entity name."""
        return self._name

    @property
    def should_poll(self) -> bool:
        """Polling needed for fan."""
        return True

    @property
    def state_attributes(self) -> dict:
        """Return optional state attributes."""
        __last_is_on = (getattr(self, 'fan_power') == 'on')
        self._state_attrs = self.fan_get_prop()
        data = {}  # type: dict

        for prop, attr in FAN_PROP_TO_ATTR.items():
            if not hasattr(self, prop):
                continue

            value = getattr(self, prop)
            if value is not None:
                data[attr] = value

        __is_on = (getattr(self, 'fan_power') == 'on')

        if (__last_is_on != __is_on):
            if (__is_on != self._is_on):
                _LOGGER.info("Sync fan status")
                self._is_on = __is_on

        return data

    @property
    def is_on(self) -> bool:
        """Return true if the entity is on."""
        return self._is_on

    @property
    def speed(self) -> str:
        """Return the current speed."""
        if (self._is_on):
            self.oscillating = (getattr(self, 'fan_natural_level') != 0)
            if (self.oscillating):
                speed_level = getattr(self, 'fan_natural_level')
                for s, s_range in FAN_NATURAL_SPEED.items():
                    if speed_level in s_range:
                        self._speed = s
                        break
            else:
                speed_level = getattr(self, 'fan_speed_level')
                for s, s_range in FAN_DIRECT_SPEED.items():
                    if speed_level in s_range:
                        self._speed = s
                        break
        else:
            self._speed = SPEED_OFF

        return self._speed

    @property
    def speed_num(self) -> int:
        """Return the current speed."""
        if (self._is_on):
            self.oscillating = (getattr(self, 'fan_natural_level') != 0)
            if (self.oscillating):
                speed_level = getattr(self, 'fan_natural_level')
                return speed_level
            else:
                speed_level = getattr(self, 'fan_speed_level')
                return speed_level
        else:
            return 0

        return self._speed

    @property
    def current_direction(self) -> str:
        """Fan direction."""
        if (getattr(self, 'fan_angle_enable') == 'off'):
            self.direction = 'forward'
        else:
            self.direction = str(getattr(self, 'fan_angle'))
        return self.direction

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return FAN_SPEED

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return SMART_MI_FAN_SUPPORT

    @property
    def fan(self):
        import miio
        if not self._fan:
            _LOGGER.info("initializing with host %s token %s" % (self.host, self.token))
            self._fan = miio.device(self.host, self.token)
        return self._fan

    @property
    def fan_temp_dec(self) -> int:
        """fan measured temprature."""
        return self._state_attrs['temp_dec']/10

    @property
    def fan_humidity(self) -> int:
        """fan measured humidity."""
        return self._state_attrs['humidity']

    @property
    def fan_angle(self) -> int:
        """fan rotate angle."""
        if (self._is_on):
            if (self._state_attrs['angle_enable'] == "on"):
                if (self._state_attrs['angle'] == 118):
                    return 120
                else:
                    return self._state_attrs['angle']
            else:
                return 0
        else:
            return 0

    @property
    def fan_speed(self) -> int:
        """don't know what does this means."""
        return self._state_attrs['speed']

    @property
    def fan_poweroff_time(self) -> int:
        """Time since turn off the power and with out AC connect."""
        return self._state_attrs['poweroff_time']

    @property
    def fan_power(self) -> str:
        """fan is power on or not."""
        return self._state_attrs['power']

    @property
    def fan_ac_power(self) -> str:
        """fan is connected to AC or not."""
        return self._state_attrs['ac_power']

    @property
    def fan_battery(self) -> int:
        """fan's battery value."""
        return self._state_attrs['battery']

    @property
    def fan_angle_enable(self) -> str:
        """fan is enable rotate or not."""
        return self._state_attrs['angle_enable']

    @property
    def fan_speed_level(self) -> int:
        """fan speed value in derect mode."""
        return self._state_attrs['speed_level']

    @property
    def fan_natural_level(self) -> int:
        """fan speed value in natural mode."""
        return self._state_attrs['natural_level']

    @property
    def fan_child_lock(self) -> str:
        """fan child lock is enabled or not."""
        return self._state_attrs['child_lock']

    @property
    def fan_buzzer(self) -> str:
        """fan buzzer is enabled or not."""
        return self._state_attrs['buzzer']

    @property
    def fan_led_b(self) -> str:
        """fan led is enabled or not."""
        return self._state_attrs['led_b']

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if (speed == '0'):
            self.turn_off()
        else:
            if (self.oscillating):
                if (speed in FAN_SPEED):
                    self.fan_set_natural_level(random.choice(FAN_NATURAL_SPEED[speed]))
                else:
                    self.fan_set_natural_level(int(speed))
            else:
                if (speed in FAN_SPEED):
                    self.fan_set_speed_level(random.choice(FAN_DIRECT_SPEED[speed]))
                else:
                    self.fan_set_speed_level(int(speed))

    def set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if (direction in ["left", "right"]):
            self.fan_set_move(direction)
        elif (direction in ["30", "60", "90", "120"]):
            if (self._is_on == False):
                self.turn_on()
            self.fan_set_angle(int(direction))
        elif (direction in ["0"]):
            self.fan_set_angle_enable("off")


    def oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        self.oscillating = oscillating
        self.set_speed(self._speed)

    def turn_on(self, speed: str=None) -> None:
        """Turn on the entity."""
        if (speed is None):
            self.fan_set_power("on")
        else:
            self.set_speed(speed)
        self._is_on = True

    def turn_off(self) -> None:
        """Turn off the entity."""
        self.fan_set_power("off")
        self._is_on = False

    def fan_get_prop(self):
        prop = self.fan.send("get_prop", ["temp_dec","humidity","angle","speed","poweroff_time","power","ac_power","battery","angle_enable","speed_level","natural_level","child_lock","buzzer","led_b"])
        _LOGGER.debug(prop)
        self._state = FanStatus(prop)
        attr = {'temp_dec': self._state.temp_dec,
                'humidity': self._state.humidity,
                'angle': self._state.angle,
                'speed': self._state.speed,
                'poweroff_time': self._state.poweroff_time,
                'power': self._state.power,
                'ac_power': self._state.ac_power,
                'battery': self._state.battery,
                'angle_enable': self._state.angle_enable,
                'speed_level': self._state.speed_level,
                'natural_level': self._state.natural_level,
                'child_lock': self._state.child_lock,
                'buzzer': self._state.buzzer,
                'led_b': self._state.led_b}
        return attr

    def fan_set_power(self, status):
        return self.fan.send("set_power", [status])

    def fan_set_natural_level(self, level):
        return self.fan.send("set_natural_level", [level])

    def fan_set_speed_level(self, level):
        return self.fan.send("set_speed_level", [level])

    def fan_set_move(self, direction):
        return self.fan.send("set_move", [direction])

    def fan_set_angle(self, angle):
        return self.fan.send("set_angle", [angle])

    def fan_set_angle_enable(self, status):
        return self.fan.send("set_angle_enable", [status])
