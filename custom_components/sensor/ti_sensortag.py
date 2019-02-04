"""
Support for TI SensorTags.
"""

import datetime
import logging
from datetime import timedelta
from typing import Tuple

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (
    ATTR_TIME, ATTR_TEMPERATURE, TEMP_CELSIUS, CONF_IP_ADDRESS)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from ti_sensortag_wifi import SensorTag

REQUIREMENTS = ['ti_sensortag_wifi==0.0.1']

_LOGGER = logging.getLogger(__name__)

ATTR_HUMIDITY = 'humidity'
ATTR_IR_TEMPERATURE = "ir-temperature"
ATTR_PRESSURE = 'pressure'
ATTR_ACCELEROMETER = 'accelerometer'
ATTR_MAGNETOMETER = 'magnetometer'
ATTR_GYROSCOPE = 'gyroscope'
ATTR_X = '_x'
ATTR_Y = '_y'
ATTR_Z = '_z'
ATTR_LIGHT = 'light'
ATTR_BUTTON = 'button'

SENSOR_TYPES = {'time': [ATTR_TIME, 's', 'calendar-clock'],
                'tmp': [ATTR_TEMPERATURE, TEMP_CELSIUS, 'mdi:thermometer'],
                'hum': [ATTR_HUMIDITY, '%', 'mdi:water-percent'],
                'ir_temp': [ATTR_IR_TEMPERATURE, TEMP_CELSIUS, 'mdi:thermometer'],
                'pres': [ATTR_PRESSURE, 'mBar', 'mdi:gauge'],
                'accel_x': [ATTR_ACCELEROMETER + ATTR_X, 'G', 'mdi:earth'],
                'accel_y': [ATTR_ACCELEROMETER + ATTR_Y, 'G', 'mdi:earth'],
                'accel_z': [ATTR_ACCELEROMETER + ATTR_Z, 'G', 'mdi:earth'],
                'magnet_x': [ATTR_MAGNETOMETER + ATTR_X, 'uT', 'mdi:magnet'],
                'magnet_y': [ATTR_MAGNETOMETER + ATTR_Y, 'uT', 'mdi:magnet'],
                'magnet_z': [ATTR_MAGNETOMETER + ATTR_Z, 'uT', 'mdi:magnet'],
                'gyro_x': [ATTR_GYROSCOPE + ATTR_X, u'\xB0/s',
                           'mdi:axis-x-rotate-clockwise'],
                'gyro_y': [ATTR_GYROSCOPE + ATTR_Y, u'\xB0/s',
                           'mdi:axis-x-rotate-clockwise'],
                'gyro_z': [ATTR_GYROSCOPE + ATTR_Z, u'\xB0/s',
                           'mdi:axis-x-rotate-clockwise'],
                'light': [ATTR_LIGHT, 'Lux', 'mdi:brightness-6'],
                'key': [ATTR_BUTTON, '', 'mdi:radiobox-marked']}

SCAN_INTERVAL = timedelta(seconds=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the SensorTag platform."""
    try:
        from ti_sensortag_wifi import SensorTag
    except OSError:
        _LOGGER.error("No TI SensorTag library was found.")
        return False

    data = SensorTagData(SensorTag(config.get(CONF_IP_ADDRESS)))

    dev = []
    for sensor_type in SENSOR_TYPES.keys():
        if sensor_type != 'time':
            dev.append(SensorTagSensor(data, sensor_type))

    add_entities(dev, True)


class SensorTagData:
    device: SensorTag
    time: datetime
    temperature: float
    ir_temperature: float
    humidity: float
    pressure: float
    accelerometer: Tuple[float, float, float]
    magnetometer: Tuple[float, float, float]
    gyroscope: Tuple[float, float, float]
    light: float
    key: int

    def __init__(self, device: SensorTag):
        self.device = device

    @Throttle(SCAN_INTERVAL)
    def update(self):
        data = self.device.update()
        self.time = data.time
        self.temperature = data.temperature
        self.ir_temperature = data.ir_temperature
        self.humidity = data.humidity
        self.pressure = data.pressure
        self.accelerometer = data.accelerometer
        self.magnetometer = data.magnetometer
        self.gyroscope = data.gyroscope
        self.light = data.light
        self.key = data.key


class SensorTagSensor(Entity):
    sensor_data: SensorTagData
    sensor_type: str
    _name: str
    _unit_of_measurement: str
    _icon: str

    def __init__(self, sensor_data: SensorTagData, sensor_type: str):
        self.sensor_data = sensor_data
        self.sensor_type = sensor_type
        self._name = SENSOR_TYPES[sensor_type][0]
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._icon = SENSOR_TYPES[sensor_type][2]
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    def update(self):
        """Get the latest data and updates the states."""
        self.sensor_data.update()

        if self.sensor_type == 'time':
            self._state = self.sensor_data.time
        if self.sensor_type == 'tmp':
            self._state = self.sensor_data.temperature
        if self.sensor_type == 'hum':
            self._state = self.sensor_data.humidity
        if self.sensor_type == 'ir_temp':
            self._state = self.sensor_data.ir_temperature
        if self.sensor_type == 'pres':
            self._state = self.sensor_data.pressure
        if self.sensor_type == 'accel_x':
            self._state = self.sensor_data.accelerometer[0]
        if self.sensor_type == 'accel_y':
            self._state = self.sensor_data.accelerometer[1]
        if self.sensor_type == 'accel_z':
            self._state = self.sensor_data.accelerometer[2]
        if self.sensor_type == 'magnet_x':
            self._state = self.sensor_data.magnetometer[0]
        if self.sensor_type == 'magnet_y':
            self._state = self.sensor_data.magnetometer[1]
        if self.sensor_type == 'magnet_z':
            self._state = self.sensor_data.magnetometer[2]
        if self.sensor_type == 'gyro_x':
            self._state = self.sensor_data.gyroscope[0]
        if self.sensor_type == 'gyro_y':
            self._state = self.sensor_data.gyroscope[1]
        if self.sensor_type == 'gyro_z':
            self._state = self.sensor_data.gyroscope[2]
        if self.sensor_type == 'light':
            self._state = self.sensor_data.light
        if self.sensor_type == 'key':
            self._state = self.sensor_data.key
