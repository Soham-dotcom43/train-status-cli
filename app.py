import os
from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

RAILRADAR_API_KEY = os.getenv("RAILRADAR_API_KEY")
BASE_URL = "https://api.railradar.in/v1"


def get_live_status(train_no):
    if not RAILRADAR_API_KEY:
        return {"error": "Missing RAILRADAR_API_KEY. Add it to your environment variables."}
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
    }


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/status", methods=["POST"])
def status():
    train_no = request.form.get("train_no", "").strip()
    if not train_no.isdigit():
        return render_template("index.html", error="Please enter a valid numeric train number (e.g. 12951).")
    result = get_live_status(train_no)
    if result.get("error"):
        return render_template("index.html", error=result["error"])
    return render_template("index.html", train_no=train_no, data=result)


if __name__ == "__main__":
    app.run(debug=True)
