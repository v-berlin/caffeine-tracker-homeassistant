from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_DAILY_GOAL, DEFAULT_HALF_LIFE

class CaffeineTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        from voluptuous import Schema, Coerce, Range, All, Default
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Caffeine Tracker", data=user_input)
        schema = Schema({
            "caffeine_half_life_h": All(Coerce(float), Range(min=1, max=24), Default(DEFAULT_HALF_LIFE)),
            "caffeine_daily_goal": All(Coerce(float), Range(min=10, max=1000), Default(DEFAULT_DAILY_GOAL))
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
