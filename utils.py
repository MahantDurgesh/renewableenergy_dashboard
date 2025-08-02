import requests

def recommend_energy(temp, humidity, cloud, wind, rain, has_hydro):
    if cloud < 30 and temp > 25:
        return "Solar"
    elif wind > 5:
        return "Wind"
    elif rain > 80 and has_hydro:
        return "Hydro"
    else:
        return "Grid"

def fetch_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "cloud": data["clouds"]["all"],
        "wind": data["wind"]["speed"],
        "rain": data.get("rain", {}).get("1h", 0)
    }
