import os
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

# 載入 .env 變數
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)

# ⏳ 查詢城市經緯度
def get_lat_lon(city_name):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            lat = data["results"][0]["geometry"]["location"]["lat"]
            lon = data["results"][0]["geometry"]["location"]["lng"]
            return lat, lon
        else:
            return None, None
    except requests.exceptions.RequestException:
        return None, None

# 🌤️ 查詢即時天氣
def get_weather(lat, lon):
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation_probability,relative_humidity_2m&timezone=auto"
    try:
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather = data["current_weather"]
        return {
            "temperature": weather["temperature"],
            "windspeed": weather["windspeed"],
            "time": weather["time"],
            "humidity": data["hourly"]["relative_humidity_2m"][0],
            "precipitation_probability": data["hourly"]["precipitation_probability"][0]
        }
    except requests.exceptions.RequestException:
        return None

# 🌍 網頁 UI
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form.get('city')
        lat, lon = get_lat_lon(city)
        if lat and lon:
            weather_info = get_weather(lat, lon)
            return render_template('index.html', city=city, weather=weather_info)
        else:
            return render_template('index.html', error="找不到這個城市，請重新輸入！")
    return render_template('index.html')

# 🌐 API 端點，回傳 JSON
@app.route('/api/weather', methods=['GET'])
def api_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "請提供 city 參數"}), 400
    
    lat, lon = get_lat_lon(city)
    if lat and lon:
        weather_info = get_weather(lat, lon)
        return jsonify({"city": city, "weather": weather_info})
    else:
        return jsonify({"error": "找不到這個城市"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
