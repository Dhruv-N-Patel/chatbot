import os
import streamlit as st
from groq import Groq
import googlemaps
from datetime import datetime, timedelta
import sqlite3

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY", "xxxxxxxxxxxxxxxdDf6mfgefsOUgXic"),
)

gmaps = googlemaps.Client(key='AIzaSyBxxxxxxxxxrkvvLxxxxtYxxxxx6ok')

def get_groq_response(prompt):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    return response.choices[0].message.content

def get_distance_and_time(origin, destination):
    directions = gmaps.directions(origin, destination, mode="driving")
    if directions:
        distance = directions[0]['legs'][0]['distance']['value'] / 1000  # Convert meters to km
        duration = directions[0]['legs'][0]['duration']['value'] / 60  # Convert seconds to minutes
        return distance, duration
    return None, None

def fetch_mumbai_attractions(interests, budget):
    conn = sqlite3.connect('mumbai_attractions.db')
    cursor = conn.cursor()
    query = '''
        SELECT name, type, fee, popularity, location FROM attractions
        WHERE type IN ({}) AND fee <= ?
        ORDER BY popularity DESC
    '''.format(','.join('?' for _ in interests))
    cursor.execute(query, (*interests, budget))
    attractions = cursor.fetchall()
    conn.close()
    return [{"name": a[0], "type": a[1], "fee": a[2], "popularity": a[3], "location": a[4]} for a in attractions]

def plan_itinerary(starting_point, attractions, start_time, end_time, budget):
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

st.title("Mumbai One-Day Tour Planner with Groq AI")
st.write("Plan your perfect day in Mumbai with our AI-powered assistant!")

if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {"role": "assistant", "content": "Hello! I'm here to help you plan a one-day tour. Where would you like to go, and what are your preferences?"}
    ]

for message in st.session_state.conversation:
    if message["role"] == "user":
        st.write(f"You: {message['content']}")
    else:
        st.write(f"Bot: {message['content']}")

user_input = st.text_input("Your message:", placeholder="Type your response here...")

if user_input:
    st.session_state.conversation.append({"role": "user", "content": user_input})
    
    chat_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.conversation])
    prompt = f"{chat_history}\nAssistant:"

    groq_response = get_groq_response(prompt)
    st.session_state.conversation.append({"role": "assistant", "content": groq_response})

    st.session_state["updated"] = True

starting_point = st.text_input("Starting Point:", "Mumbai CST Station")
interests = st.multiselect("Select your interests:", ["historical", "museum", "relaxing", "religious"])
budget = st.number_input("Enter your budget (in USD):", min_value=0, value=20)
start_time = st.time_input("Start Time:", value=datetime.strptime("09:00", "%H:%M").time())
end_time = st.time_input("End Time:", value=datetime.strptime("18:00", "%H:%M").time())

if st.button("Plan My Day"):
    if not interests:
        st.error("Please select at least one interest.")
    else:
        start_datetime = datetime.combine(datetime.today(), start_time)
        end_datetime = datetime.combine(datetime.today(), end_time)
        attractions = fetch_mumbai_attractions(interests, budget)
        itinerary = plan_itinerary(starting_point, attractions, start_datetime, end_datetime, budget)
        
        if itinerary:
            st.subheader("Your Itinerary:")
            for item in itinerary:
                st.write(f"**{item['name']}**")
                st.write(f"- Arrival Time: {item['arrival_time']}")
                st.write(f"- Departure Time: {item['departure_time']}")
                st.write(f"- Distance from last location: {item['distance']} km")
                st.write(f"- Travel Time: {item['travel_time']} minutes")
                st.write(f"- Entry Fee: ${item['fee']}")
                st.write(f"- Suggested Travel Mode: {item['travel_mode']}")
                st.write("---")
        else:
            st.write("No suitable attractions found for the given preferences and budget.")
