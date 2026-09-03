import os
import tkinter as tk
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
    }


class TrainStatusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Train Running Status Tracker")
        self.root.geometry("420x420")
        self.root.configure(bg="#0f172a")
        self.root.resizable(False, False)
        self._build_widgets()

    def _build_widgets(self):
        title = tk.Label(self.root, text="Train Status Tracker", font=("Segoe UI", 18, "bold"), bg="#0f172a", fg="#e2e8f0")
        title.pack(pady=(20, 5))
        subtitle = tk.Label(self.root, text="Enter a train number to check live status", font=("Segoe UI", 10), bg="#0f172a", fg="#94a3b8")
        subtitle.pack(pady=(0, 15))
        search_frame = tk.Frame(self.root, bg="#0f172a")
        search_frame.pack(pady=5)
        self.entry = tk.Entry(search_frame, font=("Segoe UI", 12), width=18, bg="#1e293b", fg="#e2e8f0", insertbackground="#e2e8f0", relief="flat")
        self.entry.pack(side="left", ipady=6, padx=(0, 8))
        self.entry.bind("<Return>", lambda event: self.search())
        search_btn = tk.Button(search_frame, text="Check", font=("Segoe UI", 10, "bold"), bg="#38bdf8", fg="#0f172a", relief="flat", padx=14, pady=6, command=self.search, cursor="hand2")
        search_btn.pack(side="left")
        self.error_label = tk.Label(self.root, text="", font=("Segoe UI", 9), bg="#0f172a", fg="#f87171", wraplength=380)
        self.error_label.pack(pady=(10, 0))
        self.card = tk.Frame(self.root, bg="#1e293b")
        self.card.pack(pady=20, padx=25, fill="both", expand=True)
        self.result_rows = {}
        fields = ["Train", "Status", "Current Station", "Delay", "Next Station"]
        for field in fields:
            row = tk.Frame(self.card, bg="#1e293b")
            row.pack(fill="x", padx=15, pady=8)
            label = tk.Label(row, text=field, font=("Segoe UI", 10), bg="#1e293b", fg="#94a3b8", anchor="w")
            label.pack(side="left")
            value = tk.Label(row, text="-", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#e2e8f0", anchor="e", wraplength=200, justify="right")
            value.pack(side="right")
            self.result_rows[field] = value

    def search(self):
        train_no = self.entry.get().strip()
        self.error_label.config(text="")
        if not train_no.isdigit():
            self.error_label.config(text="Please enter a valid numeric train number (e.g. 12951).")
            return
        self._set_loading()
        self.root.update_idletasks()
        result = get_live_status(train_no)
        if result.get("error"):
            self.error_label.config(text=result["error"])
            self._clear_results()
            return
        self._display_result(train_no, result)

    def _set_loading(self):
        for field in self.result_rows:
            self.result_rows[field].config(text="Loading...")

    def _clear_results(self):
        for field in self.result_rows:
            self.result_rows[field].config(text="-")

    def _display_result(self, train_no, data):
        delay = data["delay_minutes"]
        delay_text = f"{delay} min late" if delay and delay > 0 else "On time"
        self.result_rows["Train"].config(text=f"{train_no} - {data['train_name']}")
        self.result_rows["Status"].config(text=data["status"])
        self.result_rows["Current Station"].config(text=data["current_station"])
        self.result_rows["Delay"].config(text=delay_text, fg="#f87171" if delay and delay > 0 else "#4ade80")
        self.result_rows["Next Station"].config(text=data["next_station"])


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainStatusApp(root)
    root.mainloop()
