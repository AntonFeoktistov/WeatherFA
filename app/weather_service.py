import os

import requests
from dotenv import load_dotenv

from app.errors import LocationNotFoundError, WeatherNotFoundError
from app.schemas import LocationSchema, WeatherSchema

load_dotenv()


class WeatherFinder:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.location_url = os.getenv("OPENWEATHER_LOCATION_URL")
        self.weather_url = os.getenv("OPENWEATHER_WEATHER_URL")

    def get_weather_by_location_name(self, location_name):

        location = self._get_location_by_name(location_name)
        weather = self._get_weather_by_location(location)
        if not weather.location:
            raise WeatherNotFoundError()
        return weather

    def _get_location_by_name(self, location_name):

        params = {"q": location_name, "limit": 5, "appid": self.api_key}

        try:
            response = requests.get(self.location_url, params=params, timeout=10)
            response.raise_for_status()
            locations = response.json()

            if not locations:
                return LocationNotFoundError()

            location = locations[0]
            local_names = location.get("local_names", {})
            name_ru = local_names.get("ru", location.get("name"))

            result = {
                "lat": round(location["lat"], 3),
                "lon": round(location["lon"], 3),
                "name_en": location["name"],
                "name_ru": name_ru,
            }

            return LocationSchema.model_validate(result)

        except Exception:
            raise LocationNotFoundError()

    def _get_weather_by_location(self, location: LocationSchema):

        try:
            params = {
                "lat": location.lat,
                "lon": location.lon,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ru",
            }
            response = requests.get(self.weather_url, params=params, timeout=10)
            data = response.json()

            if data.get("cod") != 200:
                return WeatherSchema()

            result = {
                "location": location,
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
            }

            return WeatherSchema.model_validate(result)

        except Exception:
            raise WeatherNotFoundError()
