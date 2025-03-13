from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)  # 建立 Flask 伺服器
CORS(app)  # 讓手機可以存取這個伺服器

# 查詢城市經緯度
def get_lat_lon(city_name):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key=AIzaSyD5laXjfW1NUd6Xcy0SK478NRJvpY9oCpY"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "OK":
        lat = data["results"][0]["geometry"]["location"]["lat"]
        lon = data["results"][0]["geometry"]["location"]["lng"]
        return lat, lon
    return None, None

# 查詢天氣
def get_weather(lat, lon):
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
    response = requests.get(weather_url)
    data = response.json()
    return {
        "temperature": data["current_weather"]["temperature"],
        "windspeed": data["current_weather"]["windspeed"],
        "time": data["current_weather"]["time"]
    }

# 定義 API 路由
@app.route('/weather', methods=['GET'])
def weather():
    city = request.args.get('city', default="Taipei")
    lat, lon = get_lat_lon(city)
    if lat is None:
        return jsonify({"error": "City not found"}), 404
    weather_data = get_weather(lat, lon)
    return jsonify(weather_data)

# 啟動伺服器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
