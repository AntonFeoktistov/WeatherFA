from fastapi import FastAPI, Query

from app.schemas import WeatherSchema
from app.weather_service import WeatherFinder

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/home")
async def home():
    return {"message": "Home Page"}


@app.get("/weather/find", response_model=WeatherSchema)
async def find_weather(location_name: str = Query(..., max_length=30)):
    weather_finder = WeatherFinder()
    weather = weather_finder.get_weather_by_location_name(location_name)
    return weather
