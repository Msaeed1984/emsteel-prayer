import time
from datetime import datetime, timedelta
from notifier import show_notification
from prayer_calculator import calculate_prayer_times
import winsound
from tray import show_popup
import threading

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

prayer_times = {}
notified_today = set()
last_reset_date = None

# 🔥 وضع الاختبار (True = خلال 60 ثانية)
TEST_MODE = True


# =========================
# تحميل أوقات الصلاة
# =========================


def load_times():
    global prayer_times

    data = calculate_prayer_times()

    if data:
        prayer_times = data
        print("Loaded CALCULATED prayer times:", prayer_times)
    else:
        print("ERROR: Failed to calculate prayer times")


# =========================
# التحقق من الصلاة
# =========================


def check_prayer():
    now = datetime.now()

    PRAYER_ORDER = ["fajr", "dhuhr", "asr", "maghrib", "isha"]

    for name in PRAYER_ORDER:
        if name not in prayer_times:
            continue

        time_value = prayer_times[name]

        try:
            arabic_name = ARABIC_NAMES.get(name, name)

            # تحويل الوقت إلى datetime
            prayer_dt = datetime.strptime(time_value, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )

            before_5_dt = prayer_dt - timedelta(minutes=5)

            key_before_10 = f"{name}_before10"
            key_adhan = f"{name}_adhan"
            key_before = f"{name}_before"

            remaining_sec = 30

            print(name, int(remaining_sec))  # Debug

            # =========================
            # ⏳ قبل 10 دقائق
            # =========================
            if TEST_MODE:
                condition = 0 <= remaining_sec <= 60
            else:
                condition = 540 <= remaining_sec <= 600

            if condition:
                if key_before_10 not in notified_today:

                    # Popup
                    show_popup()

                    # صوت
                    play_alert_sound()

                    notified_today.add(key_before_10)

            # =========================
            # 🕌 وقت الأذان
            # =========================
            if 0 <= remaining_sec <= 30:
                if key_adhan not in notified_today:

                    play_alert_sound()

                    notified_today.add(key_adhan)

            # =========================
            # ⏳ قبل 5 دقائق
            # =========================
            if before_5_dt <= now < before_5_dt + timedelta(seconds=60):
                if key_before not in notified_today:

                    show_notification(
                        "⏳ تنبيه الصلاة", f"باقي 5 دقائق على صلاة {arabic_name}"
                    )

                    notified_today.add(key_before)

        except Exception as e:
            print("Time parse error:", e)


# =========================
# الصوت
# =========================


def play_alert_sound():
    try:
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception as e:
        print("Sound error:", e)


# =========================
# تشغيل النظام
# =========================


def run_scheduler():
    global last_reset_date

    print("Scheduler started...")
    load_times()

    while True:
        today = datetime.now().date()

        # إعادة التهيئة يومياً
        if last_reset_date != today:
            notified_today.clear()
            last_reset_date = today
            print("Reset notifications for new day")

        check_prayer()

        # تحديث الأوقات يومياً
        if datetime.now().hour == 0 and datetime.now().minute < 2:
            load_times()

        time.sleep(20)
