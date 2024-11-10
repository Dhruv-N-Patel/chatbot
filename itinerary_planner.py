
import googlemaps
import sqlite3
from datetime import datetime, timedelta

# Replace with your actual Google Maps API key
gmaps = googlemaps.Client(key='AIzaSyBU_fbPbVjsoiePqrkvvLNtDtYBhW006ok')

def get_distance_and_time(origin, destination):
    directions = gmaps.directions(origin, destination, mode="driving")
    if directions:
        distance = directions[0]['legs'][0]['distance']['value'] / 1000
        duration = directions[0]['legs'][0]['duration']['value'] / 60
        return distance, duration
    return None, None

def fetch_mumbai_attractions(interests, budget):
    conn = sqlite3.connect('mumbai_attractions.db')
    cursor = conn.cursor()
    query = f'''
        SELECT name, type, fee, popularity, location FROM attractions
        WHERE type IN ({','.join(['?' for _ in interests])}) AND fee <= ?
        ORDER BY popularity DESC
    '''
    cursor.execute(query, (*interests, budget))
    attractions = cursor.fetchall()
    conn.close()
    return [{"name": a[0], "type": a[1], "fee": a[2], "popularity": a[3], "location": a[4]} for a in attractions]

def generate_itinerary(city, interests, budget, start_time, end_time, starting_point):
    attractions = fetch_mumbai_attractions(interests, budget)
    itinerary = []
    current_time = start_time
    current_location = starting_point

    for attraction in attractions:
        distance, travel_time = get_distance_and_time(current_location, attraction["location"])
        if distance is None or travel_time is None:
            continue
        travel_mode = "taxi" if budget >= 20 else "walk"
        arrival_time = current_time + timedelta(minutes=travel_time)
        if arrival_time > end_time:
            break
        visit_duration = timedelta(hours=1)
        departure_time = arrival_time + visit_duration
        itinerary.append({
            "name": attraction["name"],
            "arrival_time": arrival_time.strftime('%H:%M'),
            "departure_time": departure_time.strftime('%H:%M'),
            "distance": distance,
            "travel_time": travel_time,
            "fee": attraction["fee"],
            "travel_mode": travel_mode
        })
        current_time = departure_time
        current_location = attraction["location"]
    return itinerary
