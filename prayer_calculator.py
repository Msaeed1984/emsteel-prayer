import json
import os
from datetime import datetime


def load_prayer_data():
    try:
        base_path = getattr(__import__("sys"), "_MEIPASS", os.path.abspath("."))
        file_path = os.path.join(base_path, "prayer_data.json")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print("Load error:", e)
        return {}


def calculate_prayer_times():
    try:
        data = load_prayer_data()

        today = datetime.now().strftime("%Y-%m-%d")

        if today in data:
            return data[today]

        print("Date not found in JSON")
        return None

    except Exception as e:
        print("Calculation error:", e)
        return None