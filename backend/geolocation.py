import sys
import os
from dotenv import load_dotenv
import requests
from typing import List, Dict

load_dotenv()
gapi = os.getenv('GOOGLE_API_KEY')

def get_nearby_restaurants(latitude: float, longitude: float, radius: int = 1000) -> List[Dict]:
    """
    Get up to 15 nearby restaurants within specified radius (default 1000 meters).
    Returns a list of dictionaries containing restaurant info including website if available.
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,
        'key': gapi,
        'type': 'restaurant'
    }
    restaurants = []
    processed_place_ids = set()
    next_page_token = None

    while len(restaurants) < 15:
        if next_page_token:
            params['pagetoken'] = next_page_token

        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] != 'OK':
            print(f"Error: {data['status']}")
            if 'error_message' in data:
                print(f"Error message: {data['error_message']}")
            break

        results = data.get('results', [])
        for result in results:
            if len(restaurants) >= 15:
                break
            
            place_id = result.get('place_id')
            if place_id and place_id not in processed_place_ids:
                processed_place_ids.add(place_id)
                restaurant = {
                    'name': result['name'],
                    'address': result.get('vicinity', 'Address not available'),
                    'website': None,
                    'distance': calculate_distance(latitude, longitude, result['geometry']['location']['lat'], result['geometry']['location']['lng'])
                }
                details = get_place_details(place_id)
                restaurant['website'] = details.get('website')
                restaurants.append(restaurant)

        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break

    return sorted(restaurants, key=lambda x: x['distance'])

def get_place_details(place_id: str) -> Dict:
    """Get additional details for a place, including website if available."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'website',
        'key': gapi
    }
    response = requests.get(url, params=params)
    result = response.json().get('result', {})
    return result

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the Haversine distance between two points on the earth."""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Radius of the Earth in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance * 1000  # Convert to meters