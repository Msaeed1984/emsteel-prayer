from datetime import datetime
from praytimes import PrayTimes


def format_time(t):
    try:
        h, m = t.split(":")
        return f"{int(h):02d}:{int(m):02d}"
    except:
        return t


def calculate_prayer_times():
    try:
        pt = PrayTimes('Makkah')

        # 🔥 ضبط دقيق للإمارات (مهم جداً)
        pt.adjust({
            'fajr': 18.2,
            'isha': 18.2
        })

        now = datetime.now()

        times = pt.getTimes(
            (now.year, now.month, now.day),
            (24.4539, 54.3773),  # أبوظبي
            4  # UTC+4
        )

        return {
            "fajr": format_time(times['fajr']),
            "dhuhr": format_time(times['dhuhr']),
            "asr": format_time(times['asr']),
            "maghrib": format_time(times['maghrib']),
            "isha": format_time(times['isha']),
        }

    except Exception as e:
        print("Calculation error:", e)
        return None