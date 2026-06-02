import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import hash_password
from app.database import Base, get_db
from app.main import app
from app.models import User
from app.schemas import LocationSchema, WeatherSchema

SQLALCHEMY_DATABASE_URL = "sqlite:///./tests/test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    user = User(name="testuser", hashed_password=hash_password("testpass123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_client(client, test_user):
    response = client.post(
        "/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def test_location():
    location = LocationSchema(
        name_en="London",
        name_ru="Лондон",
        lat=51.5,
        lon=-0.1,
    )
    weather = WeatherSchema(
        location=location,
        temperature=15.5,
        description="cloudy",
        wind_speed=5.2,
    )
    return weather


@pytest.fixture
def test_location_in_db(db_session, auth_client, test_location):
    from app.models import User
    from app.repository import LocationRepository
    from app.schemas import WeatherSchema

    user = db_session.query(User).filter(User.name == "testuser").first()
    repo = LocationRepository()

    weather = WeatherSchema(
        location=test_location.location,
        temperature=test_location.temperature,
        description=test_location.description,
        wind_speed=test_location.wind_speed,
    )

    location = repo.create_location(db_session, user, weather)
    db_session.commit()
    db_session.refresh(location)

    return location
