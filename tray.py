from logging import root

import pystray
from PIL import Image
from prayer_calculator import calculate_prayer_times
from datetime import datetime
import os
import sys
import threading
import time
from datetime import datetime, timedelta
import tkinter as tk
from PIL import Image, ImageTk

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
    "isha": ("Isha", "العشاء"),
}

ICON_MAP = {
    "fajr": "icons/fajr.png",
    "dhuhr": "icons/dhuhr.png",
    "asr": "icons/asr.png",
    "maghrib": "icons/maghrib.png",
    "isha": "icons/isha.png",
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
        months = [
            "يناير",
            "فبراير",
            "مارس",
            "أبريل",
            "مايو",
            "يونيو",
            "يوليو",
            "أغسطس",
            "سبتمبر",
            "أكتوبر",
            "نوفمبر",
            "ديسمبر",
        ]

        date_text = (
            f"📅 {days[now.weekday()]} {now.day} {months[now.month-1]} {now.year}"
        )
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
            year=now.year, month=now.month, day=now.day
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
    # 🌙 دائمًا رجّع فجر الغد
    fajr_name, fajr_time = prayer_list[0]
    tomorrow_fajr = fajr_time + timedelta(days=1)

    remaining = tomorrow_fajr - now

    return fajr_name, tomorrow_fajr.strftime("%H:%M"), remaining

    # 🌙 فجر الغد
    fajr_name, fajr_time = prayer_list[0]
    tomorrow_fajr = fajr_time + timedelta(days=1)

    remaining = tomorrow_fajr - now

    return fajr_name, tomorrow_fajr.strftime("%H:%M"), remaining


def load_icon(path, size=(40, 40)):
    try:
        path = resource_path(path)
        img = Image.open(path).resize(size)
        return ImageTk.PhotoImage(img)
    except:
        return None


# =========================
# 🔥 Tooltip
# =========================
def build_tooltip_text():
    try:
        data = calculate_prayer_times()

        if not data:
            return "EMSTEEL Prayer\nNo data"

        next_name, next_time, remaining = get_next_prayer(data)

        if not next_name:
            return "🕌 EMSTEEL Prayer\n✔ انتهت صلوات اليوم"

        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"🕌 EMSTEEL Prayer\n{format_name(next_name)} ({next_time})\n⏳ {hours:02}:{minutes:02}:{seconds:02}"

    except Exception as e:
        return "EMSTEEL Prayer"


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
    return pystray.Menu(
        pystray.MenuItem("📊 عرض الأوقات", on_click),
        pystray.MenuItem("خروج", on_exit),
    )


# =========================
# الخروج
# =========================


def on_exit(icon, item):
    icon.stop()


popup_open = False  # 🔥 حطه فوق الدالة (مرة واحدة)


def on_click(icon, item):
    global popup_open

    if popup_open:
        return

    popup_open = True
    print("🔥 OPEN CLICKED")

    def run():
        global popup_open
        try:
            show_popup()
        finally:
            popup_open = False

    run()


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


def update_tooltip(icon):
    while True:
        try:
            icon.title = build_tooltip_text()
            time.sleep(30)
        except Exception as e:
            print("Tooltip error:", e)


def show_popup():
    try:
        data = calculate_prayer_times()

        # ✅ لازم هنا (قبل أي UI)
        if not data:
            print("No prayer data")
            return

        next_name, next_time, remaining = get_next_prayer(data)

        root = tk.Tk()
        root.overrideredirect(True)
        root.configure(bg="#006eb3")

        root.after(10, lambda: root.focus_force())

        width = 420
        height = 420

        # 📍 تحديد الموقع
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x = screen_width - width - 20
        y = screen_height - height - 80

        root.geometry(f"{width}x{height}+{x}+{y}")

        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.0)

        # =====================
        # 🔥 Animation
        # =====================
        def fade_in(i=0):
            if i > 10:
                return
            root.attributes("-alpha", i / 10)
            root.after(20, lambda: fade_in(i + 1))

        fade_in()  # ✅ خارج الدالة

        # =====================
        # 🎨 HEADER
        # =====================
        header = tk.Frame(root, bg="#006eb3")
        header.pack(fill="x")

        tk.Label(
            header,
            text="🕌 EMSTEEL Prayer",
            fg="white",
            bg="#006eb3",
            font=("Segoe UI", 15, "bold"),
        ).pack(pady=12)

        # =====================
        # 🧱 GRID
        # =====================
        container = tk.Frame(root, bg="#006eb3")
        container.pack(padx=10, pady=10, fill="both", expand=True)

        PRAYER_ORDER = ["fajr", "dhuhr", "asr", "maghrib", "isha"]

        for i, key in enumerate(PRAYER_ORDER):
            if key not in data:
                continue

            is_next = key == next_name
            bg = "#53565a" if not is_next else "#16a34a"

            card = tk.Frame(container, bg=bg, bd=0, highlightthickness=0)
            card.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")

            icon_img = load_icon(ICON_MAP.get(key, ""))

            if icon_img:
                tk.Label(card, image=icon_img, bg=bg).pack(pady=(10, 0))
                card.image = icon_img

            tk.Label(
                card,
                text=format_name(key),
                fg="white",
                bg=bg,
                font=("Segoe UI", 11, "bold"),
            ).pack(pady=(4, 2))

            tk.Label(
                card,
                text=data[key],
                fg="#34d399" if is_next else "#e5e7eb",
                bg=bg,
                font=("Segoe UI", 13, "bold"),
            ).pack(pady=(0, 12))

        # responsive grid
        for i in range(3):
            container.rowconfigure(i, weight=1)
        for j in range(2):
            container.columnconfigure(j, weight=1)

        # =====================
        # 🧾 FOOTER
        # =====================
        footer = tk.Frame(root, bg="#004f88")
        footer.pack(fill="x", side="bottom")

        if next_name:
            tk.Label(
                footer,
                text=f"➡️ {format_name(next_name)} ({next_time})",
                fg="#ffffff",
                bg="#004f88",
                font=("Segoe UI", 11, "bold"),
            ).pack(pady=(8, 2))

            countdown_label = tk.Label(
                footer, fg="#ffdd00", bg="#004f88", font=("Segoe UI", 12, "bold")
            )
            countdown_label.pack(pady=(0, 10))

            def start_countdown():
                try:
                    remaining_sec = int(remaining.total_seconds())

                    def update():
                        nonlocal remaining_sec

                        if not root.winfo_exists():
                            return

                        if remaining_sec <= 0:
                            countdown_label.config(text="⏰ حان وقت الصلاة")
                            return

                        h, r = divmod(remaining_sec, 3600)
                        m, s = divmod(r, 60)

                        countdown_label.config(text=f"⏳ {h:02}:{m:02}:{s:02}")

                        remaining_sec -= 1
                        root.after(1000, update)

                    update()

                except Exception as e:
                    print("Countdown error:", e)

            start_countdown()

        # =====================
        # ❌ إغلاق
        # =====================
        def safe_close():
            if root.winfo_exists():
                root.destroy()

        root.after(20000, safe_close)  # إغلاق بعد 20 ثانية

        root.mainloop()

    except Exception as e:
        print("Popup error:", e)

    # =====================
    # 🚀 Tray
    # =====================


def run_tray():
    icon_path = resource_path("Emsteel2026.ico")

    image = (
        Image.open(icon_path).resize((64, 64)) if os.path.exists(icon_path) else None
    )

    icon = pystray.Icon(
        "EMSTEEL Prayer", icon=image, title="EMSTEEL Prayer", menu=build_menu()
    )

    icon.default = pystray.MenuItem("Open", on_click)

    threading.Thread(target=update_tooltip, args=(icon,), daemon=True).start()

    print("Tray started...")
    icon.run()
