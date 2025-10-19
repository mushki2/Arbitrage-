import os
import requests
import json
from utils import cache_data, load_cached_data

API_KEY = os.environ.get('ODDS_API_KEY', 'YOUR_ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com'

def get_sports():
    """
    Fetches the list of available sports from the Odds API.
    Caches the result to avoid redundant API calls.
    """
    cache_key = 'sports_list'
    cached_sports = load_cached_data(cache_key)
    if cached_sports:
        return cached_sports

    url = f"{BASE_URL}/v4/sports/?apiKey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        sports = response.json()
        cache_data(cache_key, sports)
        return sports
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sports: {e}")
        return None

def get_odds(sport_key, regions='us', markets='h2h,spreads,totals'):
    """
    Fetches odds for a specific sport from the Odds API.

    :param sport_key: The key of the sport (e.g., 'americanfootball_nfl').
    :param regions: A comma-separated list of regions (us, uk, eu, au).
    :param markets: A comma-separated list of markets (h2h, spreads, totals).
    :return: A dictionary containing the odds data or None if an error occurs.
    """
    url = f"{BASE_URL}/v4/sports/{sport_key}/odds"
    params = {
        'apiKey': API_KEY,
        'regions': regions,
        'markets': markets
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds for {sport_key}: {e}")
        return None

if __name__ == '__main__':
    # Example usage (for local testing)
    # Make sure to set your ODDS_API_KEY environment variable

    # 1. Get and print the list of sports
    sports_list = get_sports()
    if sports_list:
        print("Available Sports:")
        for sport in sports_list:
            print(f"- {sport['title']} (key: {sport['key']})")

    # 2. Get and print odds for a specific sport (e.g., NFL)
    # Note: You may need to check the 'key' from the sports list first
    if sports_list:
        nfl_key = 'americanfootball_nfl'
        print(f"\\nFetching odds for {nfl_key}...")
        odds_data = get_odds(nfl_key)
        if odds_data:
            print("Successfully fetched odds.")
            # Print the first event's details as an example
            if len(odds_data) > 0:
                print(json.dumps(odds_data[0], indent=2))
        else:
            print("Failed to fetch odds.")
