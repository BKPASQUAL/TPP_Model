from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GOOGLE_MAPS_API_KEY = 'AIzaSyCjlPRHMD6ztQgpxb-WfIL8HS274DIxYCA'

# Update the places list with more attractions and activities in the Galle area
places = [
    {'name': 'Unawatuna Beach', 'latitude': 6.0041, 'longitude': 80.2505, 'activities': ['beach', 'surfing']},
    {'name': 'Hikkaduwa Beach', 'latitude': 6.1399, 'longitude': 80.1021, 'activities': ['beach', 'surfing']},
    {'name': 'Mirissa Beach', 'latitude': 5.9480, 'longitude': 80.4564, 'activities': ['beach', 'surfing']},
    {'name': 'Galle Fort', 'latitude': 6.0249, 'longitude': 80.2170, 'activities': ['sightseeing', 'history', 'walk']},
    {'name': 'Japanese Peace Pagoda', 'latitude': 6.0191, 'longitude': 80.2376, 'activities': ['sightseeing', 'photography', 'meditation']},
    {'name': 'Galle Clock Tower', 'latitude': 6.0250, 'longitude': 80.2173, 'activities': ['sightseeing', 'photography']},
    {'name': 'Galle Dutch Hospital', 'latitude': 6.0273, 'longitude': 80.2183, 'activities': ['shopping', 'dining', 'sightseeing']},
    {'name': 'Rumassala', 'latitude': 6.0011, 'longitude': 80.2707, 'activities': ['hiking', 'nature', 'sightseeing']},
    {'name': 'Hikkaduwa Coral Sanctuary', 'latitude': 6.1401, 'longitude': 80.1011, 'activities': ['snorkeling', 'diving', 'nature']},
    {'name': 'Hikkaduwa Surfing Spots', 'latitude': 6.1385, 'longitude': 80.0998, 'activities': ['surfing']},
    {'name': 'Hikkaduwa Nightclubs', 'latitude': 6.1371, 'longitude': 80.1042, 'activities': ['nightlife', 'dancing']},
    {'name': 'Unawatuna Nightclubs', 'latitude': 6.0090, 'longitude': 80.2510, 'activities': ['nightlife', 'dancing']},
    {'name': 'The Everest Futsal Court Galle', 'latitude': 6.0281, 'longitude': 80.2178, 'activities': ['sports', 'futsal']},
    {'name': 'Jungle Beach', 'latitude': 6.0063, 'longitude': 80.2460, 'activities': ['beach', 'snorkeling', 'hiking']},
    {'name': 'Koggala Lake', 'latitude': 5.9972, 'longitude': 80.3203, 'activities': ['boating', 'nature', 'bird watching']},
    {'name': 'Sea Turtle Hatchery', 'latitude': 6.0770, 'longitude': 80.1402, 'activities': ['nature', 'education']},
    {'name': 'National Maritime Museum', 'latitude': 6.0250, 'longitude': 80.2174, 'activities': ['sightseeing', 'history', 'education']},
    {'name': 'Stilt Fishermen', 'latitude': 5.9800, 'longitude': 80.3600, 'activities': ['photography', 'cultural']},
    {'name': 'Martin Wickramasinghe Folk Museum', 'latitude': 5.9706, 'longitude': 80.3465, 'activities': ['sightseeing', 'history', 'cultural']}
]

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        user_location = data['location']
        preferences = data['preferences']
        max_distance = data.get('max_distance', None)
        travel_mode = data.get('travel_mode', 'driving')  # Default to driving if not specified

        recommendations = []

        for place in places:
            distance, duration = get_distance_and_duration(user_location, (place['latitude'], place['longitude']), travel_mode)
            if distance is None or duration is None:
                continue  # Skip places where distance or duration couldn't be calculated
            if max_distance is None or distance <= max_distance:
                if any(activity in place['activities'] for activity in preferences):
                    recommendations.append({
                        'name': place['name'],
                        'latitude': place['latitude'],
                        'longitude': place['longitude'],
                        'activities': place['activities'],
                        'distance': distance,
                        'duration': duration
                    })

        recommendations.sort(key=lambda x: x['distance'])
        return jsonify(recommendations)
    except Exception as e:
        app.logger.error(f"Error in /get_recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_distance_and_duration(origin, destination, mode='driving'):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={origin[0]},{origin[1]}&destinations={destination[0]},{destination[1]}&mode={mode}&departure_time=now&key={GOOGLE_MAPS_API_KEY}"
    try:
        response = requests.get(url, timeout=10)  # Set a timeout for the request
        response.raise_for_status()  # Raise an error for bad status codes
        result = response.json()
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000  # Convert meters to kilometers
            duration = result['rows'][0]['elements'][0].get('duration_in_traffic', result['rows'][0]['elements'][0]['duration'])['text']
            return distance, duration
        else:
            app.logger.error(f"Error in Distance Matrix response: {result['rows'][0]['elements'][0]['status']}")
            return None, None
    except requests.exceptions.RequestException as e:
        app.logger.error(f"HTTP Request failed: {str(e)}")
        return None, None

if __name__ == '__main__':
    app.run(debug=True, port=5001)
