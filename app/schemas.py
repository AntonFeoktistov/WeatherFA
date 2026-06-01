from pydantic import BaseModel


class LocationSchema(BaseModel):
    name_en: str = ""
    name_ru: str = ""
    lon: float = 0
    lat: float = 0


class WeatherSchema(BaseModel):
    location: LocationSchema = None
    temperature: float = 0
    description: str = ""
    wind_speed: float = 0
