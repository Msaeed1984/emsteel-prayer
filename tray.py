import pystray
from PIL import Image
from prayer_calculator import calculate_prayer_times
from datetime import datetime
import os
import sys
import threading
import time
from datetime import datetime, timedelta
# =========================
# تحميل الملفات داخل EXE
# =========================

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


# =========================
# الإعدادات
# =========================

LANGUAGE_MODE = "ar"

PRAYER_NAMES = {
    "fajr": ("Fajr", "الفجر"),
    "dhuhr": ("Dhuhr", "الظهر"),
    "asr": ("Asr", "العصر"),
    "maghrib": ("Maghrib", "المغرب"),
    "isha": ("Isha", "العشاء")
}


# =========================
# اللغة
# =========================

def format_name(key):
    en, ar = PRAYER_NAMES.get(key, (key, key))
    return ar if LANGUAGE_MODE == "ar" else en


# =========================
# التاريخ والوقت
# =========================

def get_datetime_text():
    now = datetime.now()

    if LANGUAGE_MODE == "ar":
        days = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                  "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

        date_text = f"📅 {days[now.weekday()]} {now.day} {months[now.month-1]} {now.year}"
        time_text = f"🕒 {now.strftime('%H:%M')}"
    else:
        date_text = now.strftime("📅 %A, %d %b %Y")
        time_text = now.strftime("🕒 %H:%M")

    return date_text, time_text


# =========================
# الصلاة القادمة
# =========================


def get_next_prayer(prayer_times):
    now = datetime.now()

    prayer_list = []

    for name, time_value in prayer_times.items():
        pt = datetime.strptime(time_value, "%H:%M").replace(
            year=now.year,
            month=now.month,
            day=now.day
        )
        prayer_list.append((name, pt))

    prayer_list.sort(key=lambda x: x[1])

    # 🔹 الصلاة القادمة اليوم
    for name, pt in prayer_list:
        if pt > now:
            remaining = pt - now
            return name, pt.strftime("%H:%M"), remaining

    # 🔥 انتهت الصلوات
    last_prayer = prayer_list[-1][1]

    # ⏳ أقل من 10 دقائق → لا تعرض القادمة
    if now < last_prayer + timedelta(minutes=10):
        return None, None, None

    # 🌙 فجر الغد
    fajr_name, fajr_time = prayer_list[0]
    tomorrow_fajr = fajr_time + timedelta(days=1)

    remaining = tomorrow_fajr - now

    return fajr_name, tomorrow_fajr.strftime("%H:%M"), remaining

# =========================
# تغيير اللغة
# =========================

def set_lang_ar(icon, item):
    global LANGUAGE_MODE
    LANGUAGE_MODE = "ar"
    icon.menu = build_menu()


def set_lang_en(icon, item):
    global LANGUAGE_MODE
    LANGUAGE_MODE = "en"
    icon.menu = build_menu()


# =========================
# بناء القائمة
# =========================

def build_menu():
    data = calculate_prayer_times()
    items = []

    # 🕌 العنوان
    title = "🕌 EMSTEEL أوقات الصلاة" if LANGUAGE_MODE == "ar" else "🕌 Prayer Times - EMSTEEL"
    items.append(pystray.MenuItem(title, None))

    # 📅 التاريخ والوقت
    date_text, time_text = get_datetime_text()
    items.append(pystray.MenuItem(date_text, None))
    items.append(pystray.MenuItem(time_text, None))

    items.append(pystray.Menu.SEPARATOR)

    if not data:
        msg = "⚠️ لا يوجد توقيت معتمد لهذا اليوم" if LANGUAGE_MODE == "ar" else "⚠️ No schedule for today"
        items.append(pystray.MenuItem(msg, None))
    else:
        # ⏱️ الأوقات (مرتبة)
        PRAYER_ORDER = ["fajr", "dhuhr", "asr", "maghrib", "isha"]

        for key in PRAYER_ORDER:
            if key in data:
                items.append(pystray.MenuItem(f"{format_name(key)}: {data[key]}", None))

        items.append(pystray.Menu.SEPARATOR)

        # ⏳ الصلاة القادمة (مرة واحدة فقط)
        next_name, next_time, remaining = get_next_prayer(data)

        if next_name:
            divider = "─────   الصلاة القادمة ─────"
            items.append(pystray.MenuItem(divider, None))

            items.append(
                pystray.MenuItem(f"➡️ {format_name(next_name)} ({next_time})", None)
            )

            # ⏳ حساب الوقت المتبقي
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)

            countdown = f"{hours:02}:{minutes:02}:{seconds:02}"

            items.append(
                pystray.MenuItem(f"⏳ باقي: {countdown}", None)
            )

        else:
            items.append(pystray.MenuItem("✔ انتهت صلوات اليوم", None))
    # 🔹 فاصل احترافي
    items.append(pystray.Menu.SEPARATOR)

    # 🌐 اللغة (دائمًا تظهر)
    items.append(pystray.MenuItem("🌐 Language", pystray.Menu(
        pystray.MenuItem("Arabic 🇸🇦", set_lang_ar),
        pystray.MenuItem("English 🇬🇧", set_lang_en),
    )))

    items.append(pystray.Menu.SEPARATOR)

    # 🏷️ Branding
    items.append(pystray.MenuItem("© IT Client Excellence Team", None))

    items.append(pystray.Menu.SEPARATOR)

    # ❌ خروج
    exit_label = "خروج" if LANGUAGE_MODE == "ar" else "Exit"
    items.append(pystray.MenuItem(exit_label, on_exit))

    return pystray.Menu(*items)


# =========================
# الخروج
# =========================

def on_exit(icon, item):
    icon.stop()


# =========================
# تشغيل Tray
# =========================

def refresh_menu(icon):
    while True:
        try:
            icon.menu = build_menu()
            time.sleep(60)  # تحديث كل دقيقة
        except Exception as e:
            print("Menu refresh error:", e)


def run_tray():
    icon = pystray.Icon("EMSTEEL Prayer")

    icon.icon = Image.open(resource_path("Emsteel2026.ico")).resize((64, 64))
    icon.menu = build_menu()

    # 🔥 هذا أهم سطر في المشروع كله
    threading.Thread(target=refresh_menu, args=(icon,), daemon=True).start()

    print("Tray started...")
    icon.run()