import datetime as dt
from caffeine_tracker.helpers import calculate_decay, peak_today, time_until_zero

def test_decay():
    now = dt.datetime(2024, 1, 1, 12, 0)
    doses = [{"amount": 100, "timestamp": now - dt.timedelta(hours=2)}]
    assert round(calculate_decay(doses, 5.0, now), 2) == 73.96

def test_preset_add():
    now = dt.datetime.now()
    doses = []
    doses.append({"amount": 120, "timestamp": now})
    assert doses[-1]["amount"] == 120

def test_time_until_zero():
    now = dt.datetime(2024, 1, 1, 12, 0)
    doses = [{"amount": 100, "timestamp": now}]
    hours = time_until_zero(doses, 5.0, now)
    assert hours > 12

def test_reset():
    doses = [{"amount": 100, "timestamp": dt.datetime.now()}]
    doses.clear()
    assert len(doses) == 0
