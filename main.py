#!/usr/bin/env python3
"""
Weather Information Script
Get detailed weather information for any country by name
"""

import requests
import sys
from datetime import datetime
from typing import Optional, Dict, Any

class WeatherAPI:
    """
    Handles communication with the OpenWeatherMap API.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"

    def get_coordinates(self, country_name: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates for the capital city of the country.
        """
        params = {
            'q': country_name,
            'limit': 5,
            'appid': self.api_key
        }
        try:
            response = requests.get(self.geo_url, params=params)
            response.raise_for_status()
            data = response.json()
            if not data:
                print(f"❌ No location found for '{country_name}'")
                return None
            location = data[0]
            return {
                'lat': location['lat'],
                'lon': location['lon'],
                'name': location.get('name', country_name),
                'country': location.get('country', country_name)
            }
        except requests.RequestException as e:
            print(f"❌ Error fetching coordinates: {e}")
            return None

    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """
        Get weather data using coordinates.
        """
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'en'
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error fetching weather data: {e}")
            return None

class WeatherFormatter:
    """
    Formats and displays weather information.
    """
    @staticmethod
    def display_weather(weather_data: Dict[str, Any], location_info: Dict[str, Any]) -> None:
        """
        Display weather information in a formatted way.
        """
        if not weather_data or 'main' not in weather_data:
            print("❌ No weather data available")
            return

        main = weather_data['main']
        weather = weather_data['weather'][0]
        wind = weather_data.get('wind', {})
        sys_info = weather_data.get('sys', {})

        sunrise = WeatherFormatter.format_time(sys_info.get('sunrise'))
        sunset = WeatherFormatter.format_time(sys_info.get('sunset'))

        print("\n" + "="*50)
        print(f"🌤️  WEATHER FOR {location_info['name'].upper()}, {location_info['country'].upper()}")
        print("="*50)
        print(f"📍 Location: {location_info['name']}, {location_info['country']}")
        print(f"🌡️  Temperature: {main['temp']}°C (Feels like {main['feels_like']}°C)")
        print(f"📊 Condition: {weather['description'].capitalize()}")
        print(f"📈 Min/Max: {main['temp_min']}°C / {main['temp_max']}°C")
        print(f"💧 Humidity: {main['humidity']}%")
        print(f"🌬️  Wind: {wind.get('speed', 'N/A')} m/s")
        print(f"☁️  Cloudiness: {weather_data.get('clouds', {}).get('all', 'N/A')}%")
        print(f"📊 Pressure: {main['pressure']} hPa")
        print(f"🌅 Sunrise: {sunrise}")
        print(f"🌇 Sunset: {sunset}")
        print(f"👁️  Visibility: {weather_data.get('visibility', 'N/A')} meters")
        print("="*50)
        print("💡 Weather advice:")
        WeatherFormatter.give_advice(weather_data)
        print("="*50)

    @staticmethod
    def format_time(timestamp: Optional[int]) -> str:
        """
        Convert a UNIX timestamp to a formatted time string.
        """
        if not timestamp:
            return "N/A"
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

    @staticmethod
    def give_advice(weather_data: Dict[str, Any]) -> None:
        """
        Provide weather-based advice.
        """
        temp = weather_data['main']['temp']
        condition = weather_data['weather'][0]['main'].lower()

        if temp > 30:
            print("   🥵 It's hot! Stay hydrated and avoid direct sun.")
        elif temp < 5:
            print("   🥶 It's cold! Dress warmly and stay indoors if possible.")
        else:
            print("   😊 Pleasant weather! Enjoy your day.")

        if 'rain' in condition:
            print("   🌧️  Rain expected! Don't forget your umbrella.")
        elif 'snow' in condition:
            print("   ❄️  Snowing! Drive carefully if you must go out.")
        elif 'cloud' in condition:
            print("   ☁️  Cloudy skies today.")
        else:
            print("   ☀️  Clear skies! Perfect outdoor weather.")

def get_api_key(default_key: str = "YOUR_API_KEY") -> Optional[str]:
    """
    Get API key from user or use default.
    """
    if default_key == "YOUR_API_KEY":
        print("⚠️  Please get a free API key from https://openweathermap.org/api")
        print("💡 After signing up, replace 'YOUR_API_KEY' in the script")
        return None
    return default_key

def main():
    if len(sys.argv) < 2:
        print("Usage: python weather.py <country_name>")
        print("Example: python weather.py Lebanon")
        sys.exit(1)

    country_name = ' '.join(sys.argv[1:])
    api_key = get_api_key()
    if not api_key:
        sys.exit(1)

    api = WeatherAPI(api_key)
    print(f"🔍 Searching for weather in {country_name}...")

    location_info = api.get_coordinates(country_name)
    if not location_info:
        sys.exit(1)

    weather_data = api.get_weather_data(location_info['lat'], location_info['lon'])
    if not weather_data:
        sys.exit(1)

    WeatherFormatter.display_weather(weather_data, location_info)

if __name__ == "__main__":
    main()