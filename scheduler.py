import time
from datetime import datetime

import winsound

from prayer_calculator import calculate_prayer_times
from tray import show_popup

# =========================
# إعدادات
# =========================

ARABIC_NAMES = {
    "fajr": "الفجر",
    "dhuhr": "الظهر",
    "asr": "العصر",
    "maghrib": "المغرب",
    "isha": "العشاء",
}

PRAYER_ORDER = ["fajr", "dhuhr", "asr", "maghrib", "isha"]

prayer_times = {}
notified_today = set()
last_reset_date = None


# =========================
# تحميل أوقات الصلاة
# =========================


def load_times():
    global prayer_times

    try:
        data = calculate_prayer_times()

        if data:
            prayer_times = data
            print("Loaded CALCULATED prayer times:", prayer_times)
        else:
            print("ERROR: Failed to calculate prayer times")

    except Exception as e:
        print("Load times error:", e)


# =========================
# الصوت
# =========================


def play_alert_sound(mode="normal"):
    try:
        if mode == "early":
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception as e:
        print("Sound error:", e)


# =========================
# التحقق من الصلاة
# =========================


def check_prayer():
    now = datetime.now()

    for name in PRAYER_ORDER:
        if name not in prayer_times:
            continue

        time_value = prayer_times[name]

        try:
            arabic_name = ARABIC_NAMES.get(name, name)

            prayer_dt = datetime.strptime(time_value, "%H:%M").replace(
                year=now.year,
                month=now.month,
                day=now.day,
                second=0,
                microsecond=0,
            )

            remaining_sec = int((prayer_dt - now).total_seconds())

            # 🔒 تجاهل الصلوات اللي راحت بزمن طويل
            if remaining_sec < -60:
                continue

            key_before5 = f"{name}_before5"
            key_adhan = f"{name}_adhan"

            # 🔍 Debug ذكي (فقط قريب من الحدث)
            if abs(remaining_sec) < 600:
                print(f"{name}: {remaining_sec}s")

            # =========================
            # ⏳ قبل 5 دقائق
            # =========================
            if 300 <= remaining_sec <= 360:
                if key_before5 not in notified_today:
                    print(f"5 min reminder for {arabic_name}")

                    show_popup()
                    play_alert_sound("early")

                    notified_today.add(key_before5)

            # =========================
            # 🕌 وقت الأذان
            # =========================
            if 0 <= remaining_sec <= 30:
                if key_adhan not in notified_today:
                    print(f"Adhan time reached for {arabic_name}")

                    show_popup()
                    play_alert_sound("normal")

                    notified_today.add(key_adhan)

        except Exception as e:
            print(f"Time parse error for {name}: {e}")


# =========================
# تشغيل النظام
# =========================


def run_scheduler():
    global last_reset_date

    print("Scheduler started...")
    load_times()

    while True:
        try:
            today = datetime.now().date()

            # إعادة التهيئة يومياً
            if last_reset_date != today:
                notified_today.clear()
                last_reset_date = today
                print("Reset notifications for new day")

            check_prayer()

            # تحديث الأوقات يومياً بعد منتصف الليل
            now = datetime.now()
            if now.hour == 0 and now.minute < 2:
                load_times()

        except Exception as e:
            print("Scheduler loop error:", e)

        time.sleep(20)
