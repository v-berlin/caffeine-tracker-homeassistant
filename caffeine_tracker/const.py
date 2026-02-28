DOMAIN = "caffeine_tracker"
CONF_HALF_LIFE = "caffeine_half_life_h"
DEFAULT_HALF_LIFE = 5.0

CONF_DAILY_GOAL = "caffeine_daily_goal"
DEFAULT_DAILY_GOAL = 200.0

ATTR_CAFFEINE_LEVEL = "caffeine_current_level_mg"
ATTR_CAFFEINE_PEAK = "caffeine_peak_today_mg"
ATTR_TIME_UNTIL_ZERO = "caffeine_time_until_zero"
ATTR_DAILY_GOAL = "caffeine_daily_goal_mg"

SENSOR_TYPES = [
    ATTR_CAFFEINE_LEVEL,
    ATTR_CAFFEINE_PEAK,
    ATTR_TIME_UNTIL_ZERO,
    ATTR_DAILY_GOAL
]

PRESETS = {
    "espresso": 80,
    "coffee": 120,
    "energy": 200,
    "cola": 35,
}
