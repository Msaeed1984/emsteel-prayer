from winotify import Notification, audio


def show_notification(title, message):
    try:
        toast = Notification(
            app_id="EMSTEEL Prayer",
            title=title,
            msg=message,
            duration="short"
        )

        # 🔊 صوت خفيف (اختياري لكنه احترافي)
        toast.set_audio(audio.Default, loop=False)

        toast.show()

    except Exception as e:
        print("Notification Error:", e)


# 🧪 اختبار مباشر
if __name__ == "__main__":
    show_notification("🧪 اختبار", "إذا ظهر هذا، النظام شغال 🔥")