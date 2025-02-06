from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

API_KEY = '3'
LEAGUE_ID = '4554'
YEAR = '2025'
BASE_URL = f'https://www.thesportsdb.com/api/v1/json/{API_KEY}'

last_fetched = None
events_data = None

def fetch_events():
    global last_fetched, events_data
    if last_fetched is None or datetime.now() - last_fetched > timedelta(hours=1):
        try:
            response = requests.get(f'{BASE_URL}/eventsseason.php?id={LEAGUE_ID}&s={YEAR}')
            response.raise_for_status()
            events_data = response.json().get('events')
            last_fetched = datetime.now()
        except requests.RequestException as error:
            print("Error fetching events:", error)

def get_betmgm_premier_league_nights():
    try:
        if events_data is None:
            fetch_events()  # Ensure events data is fetched before filtering

        if not events_data:
            print("No events found for the specified year.")
            return []

        premier_league_events = [
            event for event in events_data
            if "BetMGM Premier League Night" in event['strEvent'] and int(event['strEvent'].split()[-1]) <= 8
        ]

        if not premier_league_events:
            print("❌ No BetMGM Premier League Nights 1-8 found.")
            return []

        return premier_league_events

    except requests.RequestException as error:
        print("Error fetching BetMGM Premier League events:", error)
        return []

@app.route('/get-events')
def get_events():
    fetch_events()  # Ensure the data is up-to-date
    if events_data:
        return jsonify(events_data)
    else:
        return jsonify({"message": "No data available or failed to fetch."}), 500

@app.route('/get-betmgm-premier-league-nights')
def betmgm_premier_league_nights():
    events = get_betmgm_premier_league_nights()
    if events:
        return jsonify(events)
    else:
        return jsonify({"message": "No BetMGM Premier League Night events found."}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 if PORT is not set
    app.run(host='0.0.0.0', port=port, debug=True)

