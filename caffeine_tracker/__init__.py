import logging
import datetime as dt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, DEFAULT_HALF_LIFE, DEFAULT_DAILY_GOAL, PRESETS

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {
        "doses": [],
        "presets": dict(PRESETS),
        "half_life": DEFAULT_HALF_LIFE,
        "daily_goal": DEFAULT_DAILY_GOAL,
        "last_reset": dt.datetime.now()
    })
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    data = hass.data[DOMAIN]
    data["half_life"] = entry.options.get("caffeine_half_life_h", DEFAULT_HALF_LIFE)
    data["daily_goal"] = entry.options.get("caffeine_daily_goal", DEFAULT_DAILY_GOAL)
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, entry)
    )

    # Register services
    async def handle_add_custom_dose(call):
        amount = float(call.data["amount_mg"])
        now = dt.datetime.now()
        data["doses"].append({"amount": amount, "timestamp": now})

    async def handle_add_preset(call):
        preset = call.data["preset_name"]
        quantity = int(call.data.get("quantity", 1))
        if preset in data["presets"]:
            now = dt.datetime.now()
            for _ in range(quantity):
                data["doses"].append({"amount": data["presets"][preset], "timestamp": now})

    async def handle_reset_day(call):
        data["doses"].clear()
        data["last_reset"] = dt.datetime.now()

    hass.services.async_register(DOMAIN, "add_custom_dose", handle_add_custom_dose)
    hass.services.async_register(DOMAIN, "add_preset", handle_add_preset)
    hass.services.async_register(DOMAIN, "reset_day", handle_reset_day)
    return True
