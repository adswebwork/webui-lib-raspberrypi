"""System uptime, in seconds and in English.

Rescued from _archive/smarthouse/uptime.py, which had the formatting right and
everything around it wrong (it opened with a dangling `.set_pixels(...)` line).
"""

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24


def uptime_seconds():
    """Seconds since boot. Raises OSError where /proc/uptime is absent."""
    with open("/proc/uptime") as handle:
        return float(handle.read().split()[0])


def human_uptime(total_seconds=None):
    """'3 days, 4 hrs, 12 mins, 7 secs' - omitting leading zero units."""
    if total_seconds is None:
        total_seconds = uptime_seconds()

    days = int(total_seconds / DAY)
    hours = int((total_seconds % DAY) / HOUR)
    minutes = int((total_seconds % HOUR) / MINUTE)
    seconds = int(total_seconds % MINUTE)

    parts = []
    if days > 0:
        parts.append("{} {}".format(days, "day" if days == 1 else "days"))
    if parts or hours > 0:
        parts.append("{} {}".format(hours, "hr" if hours == 1 else "hrs"))
    if parts or minutes > 0:
        parts.append("{} {}".format(minutes, "min" if minutes == 1 else "mins"))
    parts.append("{} {}".format(seconds, "sec" if seconds == 1 else "secs"))
    return ", ".join(parts)
