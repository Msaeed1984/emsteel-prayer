import json
import os
import sys
from datetime import datetime


def load_prayer_data():
    try:
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(base_path, "prayer_data.json")
        print("Loading JSON from:", file_path)

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

        print("Date not found in JSON:", today)
        return None

    except Exception as e:
        print("Calculation error:", e)
        return None
