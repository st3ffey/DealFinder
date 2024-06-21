import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import openai
from configs.config import oaiapi
from backend.geolocation import *

def scrape_restaurant_website(url: str) -> str:
    """Scrape the content of a restaurant's website."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract text from the body of the webpage
        text = soup.body.get_text(separator=' ', strip=True)
        print(len(text)) # For knowledge
        # Limit the text to 4000 characters to fit within OpenAI's token limit
        return text[:4000]
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return ""

def analyze_restaurant_content(content: str) -> str:
    """Use OpenAI API to analyze restaurant content."""
    openai.api_key = oaiapi  # Replace with your actual API key
    
    prompt = f"""
    Analyze the following content from a restaurant's website and provide a summary including:
    1. Brief description of the restaurant
    2. Type of cuisine
    3. Notable menu items
    4. Any current deals or specials
    5. Any other interesting information

    Content:
    {content}
    """

    try:
        response = openai.chat.completions.create(
            model='gpt-4-1106-preview',
            temperature=0.05,
            messages=[
                {"role": "system", "content": "You are an expert in understanding content scraped from websites."},
                {"role": "user", "content": f"{prompt}"}
            ]
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error using OpenAI API: {str(e)}")
        return "Unable to analyze content."

def process_restaurants(restaurants: List[Dict]) -> None:
    """Process each restaurant, scrape its website, and analyze the content."""
    for restaurant in restaurants:
        if restaurant['website']:
            print(f"\nAnalyzing {restaurant['name']}...")
            content = scrape_restaurant_website(restaurant['website'])
            if content:
                analysis = analyze_restaurant_content(content)
                print(analysis)
            else:
                print("Unable to scrape website content.")
        else:
            print(f"\n{restaurant['name']} has no website available.")

if __name__ == "__main__":
    user_location = get_user_location()
    print(f"User location: {user_location}")
    
    restaurants = get_nearby_restaurants(user_location['latitude'], user_location['longitude'])
    print(f"Found {len(restaurants)} restaurants nearby.")
    
    process_restaurants(restaurants)