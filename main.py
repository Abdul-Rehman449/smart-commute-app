from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse  # Yeh naya import hai jo HTML show karega
import requests
import random

app = FastAPI()

# CORS settings taa ke frontend asani se baat kar sakay
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🚀 NAYA ROUTE: FRONTEND SHOW KARNE KE LIYE
# ==========================================
@app.get("/")
def serve_frontend():
    # Pehle yahan sirf "index.html" tha, ab folder ka path daal dein
    return FileResponse("frontend/index.html")

# ==========================================
# EXISTING ROUTES (SEARCH, ROUTE, WEATHER)
# ==========================================
@app.get("/search")
def search_location(q: str):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={q}&countrycodes=pk&addressdetails=1&limit=8"
    headers = {'User-Agent': 'SafarAsaan/1.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

@app.get("/get_route")
def get_route(origin: str, destination: str):
    headers = {'User-Agent': 'SafarAsaan/1.0'}
    try:
        # Origin ke coordinates nikalo (Pakistan mein)
        orig_url = f"https://nominatim.openstreetmap.org/search?format=json&q={origin}&countrycodes=pk&limit=1"
        orig_res = requests.get(orig_url, headers=headers, timeout=10).json()
        
        # Destination ke coordinates nikalo (Pakistan mein)
        dest_url = f"https://nominatim.openstreetmap.org/search?format=json&q={destination}&countrycodes=pk&limit=1"
        dest_res = requests.get(dest_url, headers=headers, timeout=10).json()

        if not orig_res or not dest_res:
            return {"status": "failed", "message": "Location not found"}

        orig_coords = {"lat": orig_res[0]["lat"], "lon": orig_res[0]["lon"]}
        dest_coords = {"lat": dest_res[0]["lat"], "lon": dest_res[0]["lon"]}

        # Traffic Hurdle ka logic
        hurdles = ["Construction 🚧", "Accident 💥", "Heavy Traffic 🛑", None, None, None]
        hurdle = random.choice(hurdles)

        return {
            "status": "success",
            "origin_coords": orig_coords,
            "dest_coords": dest_coords,
            "hurdle": hurdle
        }
    except Exception as e:
        return {"status": "failed", "message": str(e)}

@app.get("/get_weather")
def get_weather(lat: str, lon: str):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,weathercode"
    try:
        res = requests.get(url, timeout=10).json()
        if "current_weather" in res:
            temp = res["current_weather"]["temperature"]
            code = res["current_weather"]["weathercode"]
            
            # Weather ke icons
            icon = "☀️"
            if code in [1, 2, 3]: icon = "⛅"
            elif code in [45, 48]: icon = "🌫️"
            elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: icon = "🌧️"
            elif code in [71, 73, 75, 85, 86]: icon = "❄️"
            elif code in [95, 96, 99]: icon = "⛈️"

            return {
                "status": "success",
                "current_temp": temp,
                "current_icon": icon,
                "forecast": [
                    {"time": "+1h", "icon": icon, "temp": temp},
                    {"time": "+2h", "icon": icon, "temp": temp}
                ]
            }
    except Exception:
        pass
    return {"status": "failed"}
