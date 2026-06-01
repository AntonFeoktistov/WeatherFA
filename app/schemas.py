from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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


class UserSchema(BaseModel):
    name: str = Field(..., max_length=30)
    password1: str
    password2: str

    @field_validator("password2")
    @classmethod
    def validate_passwords_match(cls, value: str, info) -> str:
        password1 = info.data.get("password1")
        if password1 is not None and value != password1:
            raise ValueError("Пароли не совпадают")
        return value


class UserLogin(BaseModel):
    username: str = Field(..., max_length=30)
    password: str


class LocationOut(BaseModel):
    id: int
    name_en: str
    name_ru: str
    lat: float
    lon: float
    weather_data: dict
    weather_updated_at: datetime | None

    class Config:
        from_attributes = True
