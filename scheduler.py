import time
from datetime import datetime, timedelta
from notifier import show_notification
from prayer_calculator import calculate_prayer_times

# =========================
# إعدادات
# =========================

ARABIC_NAMES = {
    "fajr": "الفجر",
    "dhuhr": "الظهر",
    "asr": "العصر",
    "maghrib": "المغرب",
    "isha": "العشاء"
}

prayer_times = {}
notified_today = set()
last_reset_date = None


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
    now_str = datetime.now().strftime("%H:%M")

    PRAYER_ORDER = ["fajr", "dhuhr", "asr", "maghrib", "isha"]

    for name in PRAYER_ORDER:
        if name not in prayer_times:
            continue

        time_value = prayer_times[name]
        try:
            arabic_name = ARABIC_NAMES.get(name, name)

            # 🕌 وقت الصلاة
            if abs((datetime.strptime(time_value, "%H:%M") - datetime.now().replace(second=0, microsecond=0)).total_seconds()) < 60:
                key = f"{name}_adhan"

                if key not in notified_today:
                    show_notification(
                        "🕌 وقت الصلاة",
                        f"حان الآن وقت صلاة {arabic_name}"
                    )
                    notified_today.add(key)

            # ⏳ قبل الصلاة بـ 5 دقائق
            prayer_dt = datetime.strptime(time_value, "%H:%M")
            before_5 = (prayer_dt - timedelta(minutes=5)).strftime("%H:%M")

            before_dt = datetime.strptime(before_5, "%H:%M").replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )

            if abs((before_dt - datetime.now()).total_seconds()) < 60:
                key = f"{name}_before"

                if key not in notified_today:
                    show_notification(
                        "⏳ تنبيه الصلاة",
                        f"باقي 5 دقائق على صلاة {arabic_name}"
                    )
                    notified_today.add(key)

        except Exception as e:
            print("Time parse error:", e)
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

        # تحديث الأوقات مرة يومياً (اختياري ذكي)
        if datetime.now().hour == 0 and datetime.now().minute < 2:
            load_times()

        time.sleep(30)  # كل 30 ثانية (أدق بدون استهلاك)