import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

RAILRADAR_API_KEY = os.getenv("RAILRADAR_API_KEY")
BASE_URL = "https://api.railradar.in/v1"


def get_live_status(train_no):
    if not RAILRADAR_API_KEY:
        return {"error": "Missing RAILRADAR_API_KEY. Add it to your .env file."}

    url = f"{BASE_URL}/trains/{train_no}/live"
    headers = {"Authorization": f"Bearer {RAILRADAR_API_KEY}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Could not reach train status service: {e}"}

    if not payload.get("success") or not payload.get("data"):
        return {"error": "No live data found. Train may not be running today, or number is invalid."}

    d = payload["data"]
    current_location = d.get("currentLocation", {})
    next_halt = d.get("nextHalt", {})

    return {
        "train_name": d.get("trainName", "Unknown"),
        "status": d.get("status", "Unknown"),
        "current_station": current_location.get("stationName", "Unknown"),
        "delay_minutes": current_location.get("delayMinutes", 0),
        "next_station": next_halt.get("stationName", "N/A"),
        "eta_destination": "N/A",
    }


def print_status(train_no, data):
    print("\n" + "=" * 40)
    print(f"  TRAIN {train_no} — {data['train_name']}")
    print("=" * 40)
    print(f"  Status          : {data['status']}")
    print(f"  Current Station : {data['current_station']}")
    delay = data["delay_minutes"]
    delay_label = f"{delay} min late" if delay and delay > 0 else "On time"
    print(f"  Delay           : {delay_label}")
    print(f"  Next Station    : {data['next_station']}")
    print(f"  ETA (Destination): {data['eta_destination']}")
    print("=" * 40 + "\n")


def main():
    print("🚆 Train Running Status Tracker")
    print("Type a train number to check its status, or 'q' to quit.\n")

    while True:
        train_no = input("Enter train number: ").strip()

        if train_no.lower() == "q":
            print("Goodbye!")
            sys.exit(0)

        if not train_no.isdigit():
            print("⚠️  Please enter a valid numeric train number (e.g. 12951).\n")
            continue

        print("Fetching live status...")
        result = get_live_status(train_no)

        if result.get("error"):
            print(f"⚠️  {result['error']}\n")
            continue

        print_status(train_no, result)


if __name__ == "__main__":
    main()
