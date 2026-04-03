import threading
import os
import time
import shutil
import sys

from tray import run_tray
from scheduler import run_scheduler
from notifier import show_notification


# =========================
# First Run Message
# =========================

def show_first_run_message():
    try:
        flag_file = os.path.join(os.getenv("APPDATA"), "emsteel_prayer_installed.txt")

        if not os.path.exists(flag_file):

            time.sleep(5)  # 🔥 زودناها (مهم)

            show_notification(
                "✅ EMSTEEL Prayer",
                "تم تثبيت برنامج أوقات الصلاة بنجاح\nPrayer App Installed Successfully"
            )

            with open(flag_file, "w") as f:
                f.write("installed")

    except Exception as e:
        print("First run error:", e)
# =========================
# 🔥 Auto Start
# =========================

def add_to_startup():
    try:
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            return  # 🔥 لا يضيف أثناء التطوير

        startup_folder = os.path.join(
            os.getenv("APPDATA"),
            r"Microsoft\Windows\Start Menu\Programs\Startup"
        )

        target_path = os.path.join(startup_folder, "Emsteel Prayer.exe")

        if not os.path.exists(target_path):
            shutil.copy(exe_path, target_path)
            print("Added to startup")

    except Exception as e:
        print("Startup error:", e)
# =========================
# تشغيل النظام
# =========================

if __name__ == "__main__":
    print("Starting Prayer App...")

    # 🔥 رسالة التثبيت
    threading.Thread(target=show_first_run_message, daemon=True).start()

    # 🔥 Auto Start
    add_to_startup()

    # 🔄 Scheduler
    t1 = threading.Thread(target=run_scheduler, daemon=True)
    t1.start()

    # 🟢 Tray
    run_tray()