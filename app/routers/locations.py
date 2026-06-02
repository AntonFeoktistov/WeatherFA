from database import get_db
from dependencies import get_current_user
from errors import LocationNotFoundError, WeatherNotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models import User
from repository import LocationRepository
from schemas import LocationOut, WeatherSchema
from sqlalchemy.orm import Session
from weather_service import WeatherFinder

router = APIRouter(prefix="/locations", tags=["locations"])
location_repo = LocationRepository()


@router.get("/find", response_model=WeatherSchema)
async def find_weather(location_name: str = Query(..., max_length=30)):
    weather_finder = WeatherFinder()
    try:
        weather = weather_finder.get_weather_by_location_name(location_name)
        return weather
    except (LocationNotFoundError, WeatherNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is not found",
        )


@router.get("/", response_model=list[LocationOut])
def get_locations(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    locations = location_repo.get_all_by_user_id(db, current_user.id)
    return locations


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_location(
    weather: WeatherSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = location_repo.get_location_by_user_id_and_name(
        db, current_user.id, weather.location.name_en
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location already exists",
        )

    location_repo.create_location(db, current_user, weather)
    db.commit()

    return {"message": "Location added successfully", "weather": weather}


@router.put("/{location_name}", status_code=status.HTTP_200_OK)
async def update_location(
    location_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = location_repo.get_location_by_user_id_and_name(
        db, current_user.id, location_name
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    weather_finder = WeatherFinder()
    try:
        weather = weather_finder.get_weather_by_location_name(location_name)
    except (LocationNotFoundError, WeatherNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not fetch weather data",
        )

    location_repo.update_location(db, current_user, weather)
    db.commit()

    return {"message": "Location updated successfully", "weather": weather}


@router.delete("/{location_name}", status_code=status.HTTP_200_OK)
async def delete_location(
    location_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = location_repo.get_location_by_user_id_and_name(
        db, current_user.id, location_name
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    location_repo.delete_location(db, current_user, location_name)
    db.commit()

    return {"message": "Location deleted successfully", "location_name": location_name}
