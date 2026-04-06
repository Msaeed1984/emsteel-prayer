import subprocess


def show_notification(title, message, type="normal"):
    try:
        # 🔥 تنظيف النص (مهم جدًا)
        title = str(title).replace('"', "'").replace("\n", " ")
        message = str(message).replace('"', "'").replace("\n", " ")

        script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02
        $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template)

        $texts = $xml.GetElementsByTagName("text")
        $texts[0].AppendChild($xml.CreateTextNode("{title}")) > $null
        $texts[1].AppendChild($xml.CreateTextNode("{message}")) > $null

        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("EMSTEEL Prayer")
        $notifier.Show($toast)
        """

        subprocess.run(
            ["powershell", "-Command", script], capture_output=True, text=True
        )

    except Exception as e:
        print("Notification Error:", e)
