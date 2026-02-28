import logging
import datetime as dt
from homeassistant.components.sensor import SensorEntity
from .const import (
    DOMAIN, SENSOR_TYPES, DEFAULT_HALF_LIFE, DEFAULT_DAILY_GOAL,
    ATTR_CAFFEINE_LEVEL, ATTR_CAFFEINE_PEAK, ATTR_TIME_UNTIL_ZERO, ATTR_DAILY_GOAL
)
from .helpers import calculate_decay, peak_today, time_until_zero

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN]
    entities = [CaffeineSensor(hass, sensor, data) for sensor in SENSOR_TYPES]
    async_add_entities(entities)
    # Optional: periodically update
    async def update_all(now):
        for e in entities:
            await e.async_update_ha_state(True)
    hass.helpers.event.async_track_time_interval(update_all, dt.timedelta(minutes=1))

class CaffeineSensor(SensorEntity):
    def __init__(self, hass, sensor_type, data):
        self.hass = hass
        self._type = sensor_type
        self._attr_name = sensor_type
        self._state = 0
        self._data = data

    @property
    def state(self):
        doses = self._data["doses"]
        now = dt.datetime.now()
        half_life = self._data.get("half_life", DEFAULT_HALF_LIFE)
        if self._type == ATTR_CAFFEINE_LEVEL:
            return round(calculate_decay(doses, half_life, now), 2)
        if self._type == ATTR_CAFFEINE_PEAK:
            return round(peak_today(doses, half_life, now), 1)
        if self._type == ATTR_TIME_UNTIL_ZERO:
            return time_until_zero(doses, half_life, now)
        if self._type == ATTR_DAILY_GOAL:
            return self._data.get("daily_goal", DEFAULT_DAILY_GOAL)
        return self._state
