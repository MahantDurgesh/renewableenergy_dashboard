import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from utils import fetch_weather, recommend_energy
from datetime import datetime

st.set_page_config(page_title="Renewable Energy Advisor", layout="wide")
st.title("🌱 Distributed Renewable Energy Advisor for Indian Cities")

# API Key (get your own from https://openweathermap.org/)
OPENWEATHER_API_KEY = "243fb37e942cae0d462d3c8a769b75fc"

# Load city list
city_df = pd.read_csv("cities.csv")
city_list = city_df["City"].tolist()

# Session state for history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Sidebar Inputs
st.sidebar.header("Select City")
city = st.sidebar.selectbox("City", city_list)
hydro = st.sidebar.checkbox("Nearby Hydro Source", False)

# Real-time weather
st.sidebar.subheader("Get Real-Time Weather?")
use_api = st.sidebar.checkbox("Fetch from OpenWeatherMap", value=True)

if use_api:
    weather = fetch_weather(city, OPENWEATHER_API_KEY)
    if weather:
        temp = weather["temp"]
        humidity = weather["humidity"]
        cloud = weather["cloud"]
        wind = weather["wind"]
        rain = weather["rain"]
        st.sidebar.markdown("✅ Weather Fetched!")
    else:
        st.sidebar.error("Failed to fetch weather.")
        use_api = False
else:
    temp = st.sidebar.slider("Temperature (°C)", 0, 50, 30)
    humidity = st.sidebar.slider("Humidity (%)", 0, 100, 60)
    cloud = st.sidebar.slider("Cloud Cover (%)", 0, 100, 20)
    wind = st.sidebar.slider("Wind Speed (m/s)", 0, 15, 4)
    rain = st.sidebar.slider("Rainfall (mm)", 0, 500, 50)

# Recommendation
energy = recommend_energy(temp, humidity, cloud, wind, rain, hydro)
st.success(f"🔋 Recommended for **{city}**: **{energy}**")

# Log to history
st.session_state["history"].append({
    "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "City": city,
    "Temp (°C)": temp,
    "Humidity (%)": humidity,
    "Cloud (%)": cloud,
    "Wind (m/s)": wind,
    "Rain (mm)": rain,
    "Hydro": "Yes" if hydro else "No",
    "Energy": energy
})

# Climate Chart
st.subheader("📊 Climate Overview")
chart_df = pd.DataFrame({
    "Factor": ["Temperature", "Humidity", "Cloud", "Wind", "Rain"],
    "Value": [temp, humidity, cloud, wind, rain]
})
fig = px.bar(chart_df, x="Factor", y="Value", color="Factor")
st.plotly_chart(fig, use_container_width=True)

# Map View
st.subheader("🗺️ City Location Map")
coords = city_df[city_df["City"] == city][["Latitude", "Longitude"]].values[0]
m = folium.Map(location=coords, zoom_start=6)
folium.Marker(coords, tooltip=city, popup=f"{city}: {energy}",
              icon=folium.Icon(color="green", icon="info-sign")).add_to(m)
st_folium(m, width=700, height=500)

# History Table
st.subheader("📜 Recommendation History")
hist_df = pd.DataFrame(st.session_state["history"])
st.dataframe(hist_df)

# Report Download
st.subheader("📄 Download Report")
report = f"""
City: {city}
Temperature: {temp} °C
Humidity: {humidity} %
Cloud Cover: {cloud} %
Wind Speed: {wind} m/s
Rainfall: {rain} mm
Hydro Source: {"Yes" if hydro else "No"}

✅ Recommended Energy Source: {energy}
"""
st.download_button("Download Report", report, file_name=f"{city}_report.txt")
