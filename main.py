from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_coordinates(location_name):
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
    headers = {"User-Agent": "SmartCommuteAI_Project"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])} if data else None
    except: return None

@app.get("/get_route")
def get_route(origin: str, destination: str):
    origin_coords = get_coordinates(origin)
    dest_coords = get_coordinates(destination)
    if not origin_coords or not dest_coords:
        return {"status": "error", "message": "Location not found!"}
    
    hurdles = ["Road Closed", "Heavy Rain", "Accident", "Protest"]
    has_hurdle = random.choice([True, False, False, False])
    
    return {
        "status": "success",
        "origin_coords": origin_coords,
        "dest_coords": dest_coords,
        "hurdle": random.choice(hurdles) if has_hurdle else None
    }

@app.get("/get_weather")
def get_weather(lat: float, lon: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        
        current_temp = data["current_weather"]["temperature"]
        current_icon = "☀️" if current_temp > 25 else "⛅" if current_temp > 15 else "❄️"

        times = data["hourly"]["time"]
        temps = data["hourly"]["temperature_2m"]
        current_time = data["current_weather"]["time"]
        
        try: start_idx = times.index(current_time) + 1
        except: start_idx = 0

        forecast = []
        for i in range(start_idx, start_idx + 4):
            time_str = str(times[i]).split("T")[1] 
            t = temps[i]
            forecast.append({"time": time_str, "temp": t, "icon": "☀️" if t > 25 else "⛅" if t > 15 else "🌧️"})

        return {"status": "success", "current_temp": current_temp, "current_icon": current_icon, "forecast": forecast}
    except: return {"status": "error"}

# 🌟 NAYA FEATURE: Super Fast Search (Sirf Pakistan Ke Liye) 🌟
@app.get("/search")
def search_location(q: str):
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=5&addressdetails=1&countrycodes=pk"
    headers = {"User-Agent": "SmartCommuteAI_Project"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response.json()
    except: return []