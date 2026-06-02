import logging
import os
import socket
import time

import requests
from dotenv import load_dotenv
from pydantic import ValidationError

from app.errors import (
    LocationNotFoundError,
    WeatherNotFoundError,
    WeatherServiceUnavailableError,
)
from app.schemas import LocationSchema, WeatherSchema

load_dotenv()

logger = logging.getLogger(__name__)

_CONNECT_TIMEOUT = float(os.getenv("OPENWEATHER_CONNECT_TIMEOUT", "5"))
_READ_TIMEOUT = float(os.getenv("OPENWEATHER_READ_TIMEOUT", "60"))
_REQUEST_RETRIES = int(os.getenv("OPENWEATHER_RETRIES", "5"))
_REQUEST_TIMEOUT = (_CONNECT_TIMEOUT, _READ_TIMEOUT)
_RETRY_BACKOFF_BASE = float(os.getenv("OPENWEATHER_RETRY_BACKOFF", "1.0"))


def _force_ipv4() -> None:
    """Many VPS have broken IPv6 routes; OpenWeather then hangs until timeout."""
    import urllib3.util.connection as urllib3_connection

    def allowed_gai_family():
        return socket.AF_INET

    urllib3_connection.allowed_gai_family = allowed_gai_family


if os.getenv("OPENWEATHER_FORCE_IPV4", "1") != "0":
    _force_ipv4()


def _new_http_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Connection": "close"})
    return session


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

    def _http_get(self, url: str, params: dict) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(1, _REQUEST_RETRIES + 1):
            if attempt > 1:
                delay = _RETRY_BACKOFF_BASE * (2 ** (attempt - 2))
                logger.info("OpenWeather retry in %.1fs (attempt %s)", delay, attempt)
                time.sleep(delay)

            started = time.monotonic()
            session = _new_http_session()
            try:
                response = session.get(url, params=params, timeout=_REQUEST_TIMEOUT)
                response.raise_for_status()
                logger.info(
                    "OpenWeather OK in %.2fs (attempt %s): %s",
                    time.monotonic() - started,
                    attempt,
                    url,
                )
                return response
            except requests.Timeout as exc:
                last_error = exc
                logger.warning(
                    "OpenWeather timeout after %.2fs (attempt %s/%s): %s",
                    time.monotonic() - started,
                    attempt,
                    _REQUEST_RETRIES,
                    url,
                )
            except requests.RequestException as exc:
                last_error = exc
                logger.warning(
                    "OpenWeather error after %.2fs (attempt %s/%s): %s — %s",
                    time.monotonic() - started,
                    attempt,
                    _REQUEST_RETRIES,
                    url,
                    exc,
                )
            finally:
                session.close()

        raise WeatherServiceUnavailableError() from last_error

    def _get_location_by_name(self, location_name):
        params = {"q": location_name, "limit": 5, "appid": self.api_key}

        try:
            response = self._http_get(self.location_url, params)
            locations = response.json()

            if not locations:
                raise LocationNotFoundError()

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

        except WeatherServiceUnavailableError:
            raise
        except (requests.HTTPError, requests.RequestException, ValidationError, KeyError):
            raise LocationNotFoundError() from None

    def _get_weather_by_location(self, location: LocationSchema):
        params = {
            "lat": location.lat,
            "lon": location.lon,
            "appid": self.api_key,
            "units": "metric",
            "lang": "ru",
        }

        try:
            response = self._http_get(self.weather_url, params)
            data = response.json()

            if str(data.get("cod")) != "200":
                logger.warning("OpenWeather weather bad cod: %s", data.get("cod"))
                return WeatherSchema()

            result = {
                "location": location,
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
            }

            return WeatherSchema.model_validate(result)

        except WeatherServiceUnavailableError:
            raise
        except (requests.RequestException, ValidationError, KeyError, IndexError):
            raise WeatherNotFoundError() from None
