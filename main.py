from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.geolocation import get_nearby_restaurants
from backend.scraper import process_restaurants
import logging

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return app.send_static_file('web.html')

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    restaurants = get_nearby_restaurants(float(latitude), float(longitude))
    analyzed_restaurants = process_restaurants(restaurants)
    return jsonify(analyzed_restaurants)

if __name__ == '__main__':
    app.run(debug=True)