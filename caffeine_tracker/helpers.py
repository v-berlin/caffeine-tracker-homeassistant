import datetime as dt

def calculate_decay(doses, half_life, now=None):
    """Sum all doses with exponential decay formula."""
    if now is None:
        now = dt.datetime.now()
    total = 0.0
    for dose in doses:
        elapsed = (now - dose["timestamp"]).total_seconds() / 3600.0
        if elapsed < 0:
            elapsed = 0.0
        total += dose["amount"] * (0.5 ** (elapsed / half_life))
    return max(0.0, total)

def peak_today(doses, half_life, now=None):
    if now is None:
        now = dt.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    timeline = [midnight + dt.timedelta(minutes=m) for m in range(0, (now - midnight).seconds // 60 + 1, 10)]
    peak = 0.0
    for t in timeline:
        v = calculate_decay([d for d in doses if d["timestamp"] <= t], half_life, t)
        if v > peak:
            peak = v
    return peak

def time_until_zero(doses, half_life, now=None, threshold=1.0):
    if now is None:
        now = dt.datetime.now()
    hours = 0
    value = calculate_decay(doses, half_life, now)
    while value > threshold and hours < 48:
        hours += 0.2
        value = calculate_decay(doses, half_life, now + dt.timedelta(hours=hours))
    return round(hours,1)
