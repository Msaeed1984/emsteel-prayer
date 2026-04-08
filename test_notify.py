import tkinter as tk
from datetime import datetime


def test_alert():
    COLORS = {
        "success": "#5bc500",
        "white": "#ffffff",
    }

    root = tk.Tk()
    root.overrideredirect(True)
    root.configure(bg=COLORS["success"])
    root.attributes("-topmost", True)

    # أبعاد مناسبة (أقل ارتفاعاً بعد حذف الوقت)
    w, h = 210, 130  # قللت الارتفاع لأن الوقت حذف
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    x = sw - w - 20
    y = sh - h - 60
    root.geometry(f"{w}x{h}+{x}+{y}")

    # زر الإغلاق
    def close():
        root.destroy()

    close_btn = tk.Button(
        root,
        text="✕",
        command=close,
        fg=COLORS["white"],
        bg=COLORS["success"],
        font=("Segoe UI", 10, "bold"),
        bd=0,
        padx=7,
        pady=1,
        cursor="hand2",
        activebackground="#4a9e00",
        activeforeground=COLORS["white"],
    )
    close_btn.place(x=w - 24, y=4)

    # إطار المحتوى
    content = tk.Frame(root, bg=COLORS["success"])
    content.place(relx=0.5, y=38, anchor="n")

    # أيقونة
    icon = tk.Label(
        content,
        text="🕌",
        font=("Segoe UI", 28),
        fg=COLORS["white"],
        bg=COLORS["success"],
    )
    icon.pack(pady=(0, 8))

    # نص الصلاة
    prayer_text = tk.Label(
        content,
        text="🧪 Maghrib Azan",
        font=("Segoe UI", 10, "bold"),
        fg=COLORS["white"],
        bg=COLORS["success"],
    )
    prayer_text.pack(pady=(0, 0))

    # إغلاق تلقائي بعد 5 ثواني
    root.after(5000, close)

    root.mainloop()


if __name__ == "__main__":
    print("🧪 اختبار كرت الأذان (بدون وقت)")
    test_alert()
