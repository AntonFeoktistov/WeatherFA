from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import Base, engine, get_db
from app.repository import UserRepository
from app.schemas import UserLogin, UserSchema, WeatherSchema
from app.weather_service import WeatherFinder

app = FastAPI()
user_repo = UserRepository()
Base.metadata.create_all(bind=engine)


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


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserSchema, db: Session = Depends(get_db)):
    user = user_repo.get_user_by_name(db, user_data.name)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this name already exists",
        )
    hashed_password = hash_password(user_data.password1)
    user = user_repo.create_user(db, user_data.name, hashed_password)

    db.commit()
    return {"message": "User created successfully", "username": user_data.name}


@app.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = user_repo.get_user_by_name(db, user_data.username)

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}
