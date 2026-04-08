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
import json
import winsound
import tempfile
import atexit
import signal

# =========================
# منع التشغيل المكرر (Single Instance Protection)
# =========================


def check_single_instance():
    """التحقق من عدم وجود نسخة أخرى من البرنامج قيد التشغيل"""
    lock_file = os.path.join(tempfile.gettempdir(), "EMSTEEL_Prayer.lock")

    try:
        if os.path.exists(lock_file):
            with open(lock_file, "r") as f:
                pid = int(f.read().strip())

            try:
                import subprocess

                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True
                )

                if str(pid) in result.stdout and "EMSTEEL" in result.stdout:
                    print("⚠️ البرنامج قيد التشغيل بالفعل!")
                    try:
                        import ctypes

                        ctypes.windll.user32.MessageBoxW(
                            0,
                            "✅ EMSTEEL Prayer Agent is already running!\n\n"
                            + "البرنامج قيد التشغيل بالفعل!",
                            "EMSTEEL Prayer Agent",
                            0x40,
                        )
                    except:
                        pass
                    sys.exit(0)
                else:
                    os.remove(lock_file)
            except:
                try:
                    os.remove(lock_file)
                except:
                    pass

        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))

        return lock_file

    except Exception as e:
        print(f"⚠️ تحذير: خطأ في التحقق من النسخة الواحدة: {e}")
        return None


# =========================
# تنظيف الملفات عند الإغلاق (Cleanup)
# =========================


def cleanup_on_exit(lock_file=None):
    """تنظيف الملفات المؤقتة عند إغلاق البرنامج"""
    print("🧹 جاري تنظيف الملفات المؤقتة...")

    if lock_file and os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print("✓ تم حذف ملف القفل")
        except Exception as e:
            print(f"⚠️ خطأ في حذف ملف القفل: {e}")

    temp_dir = tempfile.gettempdir()
    temp_files = [
        f
        for f in os.listdir(temp_dir)
        if f.startswith("EMSTEEL_") and f.endswith(".tmp")
    ]

    for temp_file in temp_files:
        try:
            os.remove(os.path.join(temp_dir, temp_file))
            print(f"✓ تم حذف الملف المؤقت: {temp_file}")
        except:
            pass

    print("🧹 اكتمل التنظيف!")
    print("👋 EMSTEEL Prayer Agent closed successfully")


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

LANGUAGE_MODE = "en"
SOUND_ENABLED = True
SETTINGS_FILE = "prayer_settings.json"

# متغيرات لمنع تكرار الأذان
LAST_ALERT_TIME = {}
ALERT_COOLDOWN = 55

# متغيرات فترة ما بعد الأذان (AZAN TIME NOW لمدة 5 دقائق)
POST_ADHAN_DURATION = 5  # عدد الدقائق
post_adhan_active = False
post_adhan_start_time = None
post_adhan_prayer_name = None


def load_settings():
    global LANGUAGE_MODE, SOUND_ENABLED
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                LANGUAGE_MODE = settings.get("language", "en")
                SOUND_ENABLED = settings.get("sound", True)
    except:
        pass


def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "language": LANGUAGE_MODE,
                    "sound": SOUND_ENABLED,
                },
                f,
            )
    except:
        pass


load_settings()

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

COLORS = {
    "primary": "#006eb3",
    "success": "#5bc500",
    "gray": "#53565A",
    "white": "#ffffff",
}


def format_name(key):
    en, ar = PRAYER_NAMES.get(key, (key, key))
    return ar if LANGUAGE_MODE == "ar" else en


def get_text(key):
    texts = {
        "show_times": {"en": "📊 Show Prayer Times", "ar": "📊 عرض أوقات الصلاة"},
        "sound_on": {"en": "🔊 Sound: ON", "ar": "🔊 الصوت: تشغيل"},
        "sound_off": {"en": "🔇 Sound: OFF", "ar": "🔇 الصوت: إيقاف"},
        "language_english": {"en": "🌐 English", "ar": "🌐 English"},
        "language_arabic": {"en": "🌐 العربية", "ar": "🌐 العربية"},
        "exit": {"en": "🚪 Exit", "ar": "🚪 خروج"},
        "next_prayer": {"en": "NEXT PRAYER", "ar": "الصلاة القادمة"},
        "azan_time_now": {"en": "🔔 AZAN TIME NOW!", "ar": "🔔 وقت الأذان الآن!"},
    }
    return texts.get(key, {}).get(LANGUAGE_MODE, key)


def get_next_prayer(prayer_times):
    """حساب أقرب صلاة قادمة"""
    now = datetime.now()
    prayer_list = []

    for name, time_value in prayer_times.items():
        pt = datetime.strptime(time_value, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        prayer_list.append((name, pt))

    prayer_list.sort(key=lambda x: x[1])

    for name, pt in prayer_list:
        if pt > now:
            remaining = pt - now
            return name, pt.strftime("%H:%M"), remaining

    # إذا انتهت جميع صلوات اليوم، خذ فجر الغد
    fajr_name, fajr_time = prayer_list[0]
    tomorrow_fajr = fajr_time + timedelta(days=1)
    remaining = tomorrow_fajr - now
    return fajr_name, tomorrow_fajr.strftime("%H:%M"), remaining


def load_icon(path, size=(35, 35)):
    try:
        path = resource_path(path)
        img = Image.open(path).resize(size)
        return ImageTk.PhotoImage(img)
    except:
        return None


def play_prayer_sound():
    if not SOUND_ENABLED:
        return
    try:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except:
        pass


# ============================================================
# كرت الأذان
# ============================================================


def show_alert_popup(prayer_name, prayer_time):
    """إظهار نافذة منبثقة عند وقت الأذان"""

    def run_alert():
        try:
            alert_root = tk.Tk()
            alert_root.overrideredirect(True)
            alert_root.configure(bg=COLORS["success"])
            alert_root.attributes("-topmost", True)

            w, h = 200, 120
            sw, sh = alert_root.winfo_screenwidth(), alert_root.winfo_screenheight()
            x = sw - w - 20
            y = sh - h - 60
            alert_root.geometry(f"{w}x{h}+{x}+{y}")

            def close_alert():
                alert_root.destroy()

            close_btn = tk.Button(
                alert_root,
                text="✕",
                command=close_alert,
                fg=COLORS["white"],
                bg=COLORS["success"],
                font=("Segoe UI", 9, "bold"),
                bd=0,
                padx=6,
                pady=1,
                cursor="hand2",
                activebackground="#4a9e00",
                activeforeground=COLORS["white"],
            )
            close_btn.place(x=w - 22, y=3)

            content = tk.Frame(alert_root, bg=COLORS["success"])
            content.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(
                content,
                text="🕌",
                font=("Segoe UI", 28),
                fg=COLORS["white"],
                bg=COLORS["success"],
            ).pack(pady=(0, 8))

            if LANGUAGE_MODE == "ar":
                prayer_text = f"أذان {format_name(prayer_name)}"
            else:
                prayer_text = f"{format_name(prayer_name)} Azan"

            tk.Label(
                content,
                text=prayer_text,
                font=("Segoe UI", 10, "bold"),
                fg=COLORS["white"],
                bg=COLORS["success"],
            ).pack()

            alert_root.after(5000, close_alert)
            play_prayer_sound()
            alert_root.mainloop()

        except Exception as e:
            print(f"Alert error: {e}")

    threading.Thread(target=run_alert, daemon=True).start()


# ============================================================
# دوال البرنامج الرئيسية
# ============================================================


def update_post_adhan_timer():
    """تحديث مؤقت ما بعد الأذان"""
    global post_adhan_active, post_adhan_start_time, post_adhan_prayer_name

    if post_adhan_active and post_adhan_start_time:
        elapsed = (datetime.now() - post_adhan_start_time).total_seconds() / 60
        if elapsed >= POST_ADHAN_DURATION:
            post_adhan_active = False
            post_adhan_start_time = None
            post_adhan_prayer_name = None
            print(
                f"⏰ انتهت فترة {POST_ADHAN_DURATION} دقائق بعد أذان {post_adhan_prayer_name}، العودة للعداد العادي"
            )


def check_prayer_time():
    """التحقق من وقت الصلاة وإظهار التنبيه - مع منع التكرار وتفعيل مؤقت ما بعد الأذان"""
    global LAST_ALERT_TIME, post_adhan_active, post_adhan_start_time, post_adhan_prayer_name

    try:
        data = calculate_prayer_times()
        if data:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_timestamp = now.timestamp()

            for name, pt in data.items():
                if pt == current_time:
                    last_alert = LAST_ALERT_TIME.get(name, 0)
                    if current_timestamp - last_alert > ALERT_COOLDOWN:
                        LAST_ALERT_TIME[name] = current_timestamp
                        post_adhan_active = True
                        post_adhan_start_time = now
                        post_adhan_prayer_name = name
                        print(
                            f"🔔 أذان {name} الساعة {pt} - سيبقى 'AZAN TIME NOW' لمدة {POST_ADHAN_DURATION} دقائق"
                        )
                        show_alert_popup(name, pt)
    except Exception as e:
        print(f"Error in check_prayer_time: {e}")

    threading.Timer(60, check_prayer_time).start()


def build_tooltip_text():
    """بناء نص الأداة المنبثقة (Tooltip) - مع دعم فترة AZAN TIME NOW"""
    global post_adhan_active

    try:
        data = calculate_prayer_times()
        if not data:
            return "EMSTEEL Prayer\nNo data"

        # تحديث مؤقت ما بعد الأذان
        update_post_adhan_timer()

        # إذا كان مؤقت ما بعد الأذان نشطاً
        if post_adhan_active:
            if LANGUAGE_MODE == "ar":
                return f"EMSTEEL Prayer\n🔔 وقت الأذان الآن!"
            else:
                return f"EMSTEEL Prayer\n🔔 AZAN TIME NOW!"

        # العداد العادي
        next_name, next_time, remaining = get_next_prayer(data)

        if not next_name:
            return "EMSTEEL Prayer\n✔ انتهت صلوات اليوم"

        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        if LANGUAGE_MODE == "ar":
            if next_name == "fajr":
                return f"EMSTEEL Prayer\n🌙 حتى الفجر: {hours:02}:{minutes:02}:{seconds:02}"
            else:
                return f"EMSTEEL Prayer\n{format_name(next_name)} ({next_time})\n⏳ {hours:02}:{minutes:02}:{seconds:02}"
        else:
            if next_name == "fajr":
                return f"EMSTEEL Prayer\n🌙 Until Fajr: {hours:02}:{minutes:02}:{seconds:02}"
            else:
                return f"EMSTEEL Prayer\n{format_name(next_name)} ({next_time})\n⏳ {hours:02}:{minutes:02}:{seconds:02}"
    except:
        return "EMSTEEL Prayer"


def update_tooltip(icon):
    while True:
        try:
            icon.title = build_tooltip_text()
            time.sleep(1)
        except:
            time.sleep(1)


def show_popup_callback(icon=None, item=None):
    def run_popup():
        try:
            show_popup()
        except Exception as e:
            print(f"Error: {e}")

    threading.Thread(target=run_popup, daemon=True).start()


def on_exit(icon, item):
    print("🛑 جاري إغلاق EMSTEEL Prayer Agent...")
    save_settings()
    cleanup_on_exit(lock_file)
    icon.stop()
    os._exit(0)


def toggle_sound(icon, item):
    global SOUND_ENABLED
    SOUND_ENABLED = not SOUND_ENABLED
    save_settings()
    icon.menu = create_menu()


def toggle_language(icon, item):
    global LANGUAGE_MODE
    LANGUAGE_MODE = "ar" if LANGUAGE_MODE == "en" else "en"
    save_settings()
    icon.menu = create_menu()


def create_menu():
    sound_text = get_text("sound_on") if SOUND_ENABLED else get_text("sound_off")
    if LANGUAGE_MODE == "en":
        language_text = get_text("language_arabic")
    else:
        language_text = get_text("language_english")

    return pystray.Menu(
        pystray.MenuItem(get_text("show_times"), show_popup_callback, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(sound_text, toggle_sound),
        pystray.MenuItem(language_text, toggle_language),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(get_text("exit"), on_exit),
    )


popup_open = False
popup_lock = threading.Lock()


def show_popup():
    global popup_open
    with popup_lock:
        if popup_open:
            return
        popup_open = True

    try:
        data = calculate_prayer_times()
        if not data:
            print("No prayer data")
            return

        next_name, next_time, remaining = get_next_prayer(data)

        root = tk.Tk()
        root.overrideredirect(True)
        root.configure(bg=COLORS["primary"])

        width, height = 380, 480
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = screen_width - width - 20
        y = screen_height - height - 60
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.attributes("-topmost", True)

        main = tk.Frame(root, bg=COLORS["primary"])
        main.pack(fill="both", expand=True)

        # الهيدر
        header = tk.Frame(main, bg=COLORS["primary"], height=50)
        header.pack(fill="x", padx=10, pady=(8, 5))
        header.pack_propagate(False)

        def close_window():
            global popup_open
            popup_open = False
            root.destroy()

        close_button = tk.Button(
            header,
            text="✕",
            fg=COLORS["white"],
            bg=COLORS["primary"],
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=8,
            pady=0,
            cursor="hand2",
            activebackground=COLORS["gray"],
            command=close_window,
        )
        close_button.pack(side="right")

        center_frame = tk.Frame(header, bg=COLORS["primary"])
        center_frame.pack(expand=True)

        header_icon_path = resource_path("icons/header.png")
        if os.path.exists(header_icon_path):
            try:
                img = Image.open(header_icon_path).resize(
                    (30, 30), Image.Resampling.LANCZOS
                )
                header_image = ImageTk.PhotoImage(img)
                icon_label = tk.Label(
                    center_frame, image=header_image, bg=COLORS["primary"]
                )
                icon_label.pack(side="left", padx=(0, 5))
                icon_label.image = header_image
            except:
                pass

        tk.Label(
            center_frame,
            text="EMSTEEL Prayer",
            fg=COLORS["white"],
            bg=COLORS["primary"],
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left")

        tk.Frame(main, bg=COLORS["gray"], height=1).pack(fill="x", padx=10, pady=(0, 8))

        # بطاقات الصلوات
        container = tk.Frame(main, bg=COLORS["primary"])
        container.pack(fill="both", expand=True, padx=10, pady=5)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        grid_positions = {
            "fajr": (0, 0),
            "dhuhr": (0, 1),
            "asr": (1, 0),
            "maghrib": (1, 1),
            "isha": (2, 0),
        }

        for key in ["fajr", "dhuhr", "asr", "maghrib", "isha"]:
            if key not in data:
                continue

            is_next = key == next_name
            bg = COLORS["success"] if is_next else COLORS["gray"]
            row, col = grid_positions[key]

            cell = tk.Frame(container, bg=COLORS["primary"])
            cell.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            container.rowconfigure(row, weight=1)

            card = tk.Frame(cell, bg=bg, bd=0)
            card.pack(fill="both", expand=True)

            inner = tk.Frame(card, bg=bg)
            inner.pack(fill="both", expand=True, padx=6, pady=6)

            icon_img = load_icon(ICON_MAP.get(key, ""), size=(28, 28))
            content = tk.Frame(inner, bg=bg)
            content.pack(expand=True)

            if icon_img:
                lbl = tk.Label(content, image=icon_img, bg=bg)
                lbl.pack(side="left", padx=(0, 5))
                lbl.image = icon_img

            text_frame = tk.Frame(content, bg=bg)
            text_frame.pack(side="left", expand=True)

            tk.Label(
                text_frame,
                text=format_name(key),
                fg=COLORS["white"],
                bg=bg,
                font=("Segoe UI", 8, "bold"),
                anchor="w",
            ).pack(anchor="w")
            tk.Label(
                text_frame,
                text=data[key],
                fg=COLORS["white"],
                bg=bg,
                font=("Segoe UI", 11, "bold"),
                anchor="w",
            ).pack(anchor="w")

        tk.Frame(main, bg=COLORS["gray"], height=1).pack(fill="x", padx=10, pady=(8, 5))

        # الفوتر
        footer = tk.Frame(main, bg=COLORS["primary"])
        footer.pack(fill="x", padx=10, pady=(0, 8))

        if next_name:
            next_frame = tk.Frame(footer, bg=COLORS["success"], bd=0)
            next_frame.pack(fill="x", pady=(0, 8))

            if next_name == "fajr":
                if LANGUAGE_MODE == "ar":
                    next_text = f"➡️ المتبقي حتى الفجر"
                else:
                    next_text = f"➡️ Until Fajr"
            else:
                next_text = f"➡️ {get_text('next_prayer')}: {format_name(next_name)}"

            next_label = tk.Label(
                next_frame,
                text=next_text,
                fg=COLORS["white"],
                bg=COLORS["success"],
                font=("Segoe UI", 9, "bold"),
            )
            next_label.pack(pady=(6, 0))

            time_label = tk.Label(
                next_frame,
                text=f"⏰ {next_time}",
                fg=COLORS["white"],
                bg=COLORS["success"],
                font=("Segoe UI", 13, "bold"),
            )
            time_label.pack(pady=(0, 4))

            progress_canvas = tk.Canvas(
                footer, width=340, height=4, bg=COLORS["gray"], highlightthickness=0
            )
            progress_canvas.pack(pady=(5, 0))
            progress_bar = progress_canvas.create_rectangle(
                0, 0, 0, 4, fill=COLORS["success"], outline=""
            )

            countdown_label = tk.Label(
                footer,
                fg=COLORS["white"],
                bg=COLORS["primary"],
                font=("Segoe UI", 14, "bold"),
            )
            countdown_label.pack(pady=(5, 2))

            def update_countdown():
                if not root.winfo_exists():
                    return

                nonlocal next_name, next_time
                now = datetime.now()

                new_next_name, new_next_time, new_remaining = get_next_prayer(data)

                if new_next_name != next_name or new_next_time != next_time:
                    next_name = new_next_name
                    next_time = new_next_time

                    if next_name == "fajr":
                        if LANGUAGE_MODE == "ar":
                            next_text = f"➡️ المتبقي حتى الفجر"
                        else:
                            next_text = f"➡️ Until Fajr"
                    else:
                        next_text = (
                            f"➡️ {get_text('next_prayer')}: {format_name(next_name)}"
                        )

                    next_label.config(text=next_text)
                    time_label.config(text=f"⏰ {next_time}")

                prayer_dt = datetime.strptime(next_time, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day, second=0, microsecond=0
                )

                if prayer_dt <= now:
                    prayer_dt = prayer_dt + timedelta(days=1)

                remaining_live = (prayer_dt - now).total_seconds()

                if remaining_live <= 0:
                    root.after(1000, update_countdown)
                    return

                h, r = divmod(int(remaining_live), 3600)
                m, s = divmod(r, 60)
                countdown_label.config(text=f"⏳ {h:02}:{m:02}:{s:02}")

                max_seconds = 12 * 3600
                progress = (max_seconds - remaining_live) / max_seconds * 340
                progress_canvas.coords(
                    progress_bar, 0, 0, max(0, min(340, progress)), 4
                )

                delay = 1000 if remaining_live < 3600 else 2000
                root.after(delay, update_countdown)

            update_countdown()

        controls_frame = tk.Frame(footer, bg=COLORS["primary"])
        controls_frame.pack(pady=(5, 3))

        def sound_cmd():
            global SOUND_ENABLED
            SOUND_ENABLED = not SOUND_ENABLED
            save_settings()
            btn_sound.config(
                text=get_text("sound_on") if SOUND_ENABLED else get_text("sound_off"),
                bg=COLORS["success"] if SOUND_ENABLED else COLORS["gray"],
            )

        btn_sound = tk.Button(
            controls_frame,
            text=get_text("sound_on") if SOUND_ENABLED else get_text("sound_off"),
            fg=COLORS["white"],
            bg=COLORS["success"] if SOUND_ENABLED else COLORS["gray"],
            font=("Segoe UI", 8, "bold"),
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=sound_cmd,
        )
        btn_sound.pack(side="left", padx=3)

        def lang_cmd():
            global LANGUAGE_MODE
            LANGUAGE_MODE = "ar" if LANGUAGE_MODE == "en" else "en"
            save_settings()
            close_window()
            show_popup()

        if LANGUAGE_MODE == "en":
            lang_button_text = get_text("language_arabic")
        else:
            lang_button_text = get_text("language_english")

        btn_lang = tk.Button(
            controls_frame,
            text=lang_button_text,
            fg=COLORS["white"],
            bg=COLORS["primary"],
            font=("Segoe UI", 8, "bold"),
            bd=1,
            padx=8,
            pady=4,
            cursor="hand2",
            command=lang_cmd,
        )
        btn_lang.pack(side="left", padx=3)

        tk.Label(
            footer,
            text="IT Client Excellence Team v1.0",
            fg=COLORS["white"],
            bg=COLORS["primary"],
            font=("Segoe UI", 7),
        ).pack(pady=(2, 0))

        def safe_close():
            global popup_open
            if root.winfo_exists():
                popup_open = False
                root.destroy()

        root.after(30000, safe_close)
        root.bind("<Escape>", lambda e: close_window())
        root.mainloop()

    except Exception as e:
        print(f"Popup error: {e}")
    finally:
        with popup_lock:
            popup_open = False


def run_tray():
    global lock_file

    print("=" * 50)
    print("🚀 Starting EMSTEEL Prayer Agent...")
    print("=" * 50)

    lock_file = check_single_instance()
    atexit.register(lambda: cleanup_on_exit(lock_file))

    def signal_handler(signum, frame):
        print("\n🛑 Received shutdown signal...")
        cleanup_on_exit(lock_file)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    icon_path = resource_path("Emsteel2026.ico")
    image = (
        Image.open(icon_path).resize((64, 64)) if os.path.exists(icon_path) else None
    )

    threading.Thread(target=check_prayer_time, daemon=True).start()

    icon = pystray.Icon(
        "EMSTEEL Prayer", icon=image, title="EMSTEEL Prayer", menu=create_menu()
    )
    threading.Thread(target=update_tooltip, args=(icon,), daemon=True).start()

    print("=" * 50)
    print("✅ EMSTEEL Prayer Agent Started Successfully!")
    print(f"🔊 Sound: {'ON' if SOUND_ENABLED else 'OFF'}")
    print(f"🌐 Language: {'العربية' if LANGUAGE_MODE == 'ar' else 'English'}")
    print(f"🔒 Single Instance Protection: ACTIVE")
    print(f"🧹 Cleanup on exit: ENABLED")
    print(f"⏰ Post-Adhan Display: {POST_ADHAN_DURATION} minutes")
    print("=" * 50)
    print("📌 HOW TO USE:")
    print("   • LEFT CLICK on icon → Show prayer times")
    print("   • RIGHT CLICK on icon → Show menu")
    print("   • At Azan time, popup appears and 'AZAN TIME NOW' shown for 5 min")
    print("   • After Isha, counter automatically shows time until Fajr")
    print("=" * 50)

    icon.run()


if __name__ == "__main__":
    lock_file = None
    run_tray()
