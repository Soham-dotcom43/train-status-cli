# 🚆 Train Running Status Tracker

A Python command-line app that shows live running status of Indian trains — current station, delay, and next station — using the RailRadar API.

## Features
- Enter any train number to get live status
- Shows current station, delay in minutes, and next station
- Keeps running so you can check multiple trains in one session

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Get a free API key at https://railradar.in/developers (no credit card required)
3. Create a `.env` file with: `RAILRADAR_API_KEY=your_key_here`
4. Run: `python train_status.py`
