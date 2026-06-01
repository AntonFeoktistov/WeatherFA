from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Location, User
from app.schemas import WeatherSchema


class UserRepository:
    def __init__(self):
        pass

    def get_user_by_name(self, session: Session, name: str):
        stmt = select(User).where(User.name == name)
        return session.scalars(stmt).first()

    def get_user_by_id(self, session: Session, id: int):
        stmt = select(User).where(User.id == id)
        return session.scalars(stmt).first()

    def create_user(self, session: Session, name: str, hashed_password: str):
        new_user = User(name=name, hashed_password=hashed_password)
        session.add(new_user)
        session.flush()
        return new_user


class LocationRepository:
    def __init__(self):
        pass

    def get_all_by_user_id(self, session: Session, id: int):
        stmt = select(Location).where(Location.user_id == id)
        return session.scalars(stmt).all()

    def get_location_by_user_id_and_name(self, session: Session, id: int, name: str):
        stmt = select(Location).where(Location.user_id == id, Location.name_en == name)
        return session.scalars(stmt).first()

    def create_location(self, session: Session, user: User, weather: WeatherSchema):
        loc = weather.location
        weather_data_to_add = {
            "temperature": weather.temperature,
            "description": weather.description,
            "wind_speed": weather.wind_speed,
        }
        location = Location(
            name_en=loc.name_en,
            name_ru=loc.name_ru,
            lat=loc.lat,
            lon=loc.lon,
            weather_data=weather_data_to_add,
            user_id=user.id,
        )
        session.add(location)
        session.flush()
        return location
