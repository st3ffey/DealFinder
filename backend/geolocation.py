import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import requests
from typing import List, Dict
from configs.config import gapi

def get_user_location(ip_address: str = None) -> Dict[str, float]:
    """Get user's latitude and longitude based on IP address."""
    if not ip_address:
        ip_address = requests.get('https://api.ipify.org').text

    response = requests.get(f'http://ip-api.com/json/{ip_address}')
    data = response.json()

    return {
        'latitude': data['lat'],
        'longitude': data['lon']
    }

def get_nearby_restaurants(latitude: float, longitude: float, radius: int = 1000) -> List[Dict]:
    """
    Get nearby restaurants within specified radius (default 1 mile = 1609 meters).
    Returns a list of dictionaries containing restaurant info including website if available.
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,
        'type': 'restaurant',
        'key': gapi
    }

    response = requests.get(url, params=params, verify=False)
    data = response.json()

    results = data.get('results', [])

    restaurants = []
    for result in results:
        restaurant = {
            'name': result['name'],
            'address': result.get('vicinity', 'Address not available'),
            'website': None
        }

        # If we have a place_id, we can get more details including the website
        if 'place_id' in result:
            details = get_place_details(result['place_id'])
            restaurant['website'] = details.get('website')

        restaurants.append(restaurant)

    return restaurants

def get_place_details(place_id: str) -> Dict:
    """Get additional details for a place, including website if available."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"

    params = {
        'place_id': place_id,
        'fields': 'website',
        'key': gapi
    }

    response = requests.get(url, params=params, verify=False)
    result = response.json()['result']

    return result

if __name__ == "__main__":
    user_location = get_user_location()
    print(f"User location: {user_location}")

    restaurants = get_nearby_restaurants(user_location['latitude'], user_location['longitude'])
    print(f"Found {len(restaurants)} restaurants nearby:")
    for restaurant in restaurants:
        print(f"- {restaurant['name']}: {restaurant['website']}")