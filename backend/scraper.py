import sys
import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import openai
from backend.geolocation import *
from backend.restaurant_analyzer import analyze_restaurant_content

def scrape_restaurant_website(url: str) -> str:
    """Scrape the content of a restaurant's website."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from the body of the webpage
        text = soup.body.get_text(separator=' ', strip=True)
        print(len(text)) # For knowledge
        # Limit the text to 4000 characters to fit within OpenAI's token limit
        return text[:4000]
    except requests.RequestException as e:
        print(f"Error scraping {url}: {str(e)}")
        return ""

def process_restaurants(restaurants: List[Dict]) -> List[Dict]:
    """Process each restaurant, scrape its website, and analyze the content."""
    processed_restaurants = []
    for restaurant in restaurants:
        processed_restaurant = restaurant.copy()
        if restaurant['website']:
            content = scrape_restaurant_website(restaurant['website'])
            if content:
                analysis = analyze_restaurant_content(content)
                processed_restaurant['analysis'] = analysis
            else:
                processed_restaurant['analysis'] = "Unable to scrape website content."
        else:
            processed_restaurant['analysis'] = "No website available."
        processed_restaurants.append(processed_restaurant)
    return processed_restaurants