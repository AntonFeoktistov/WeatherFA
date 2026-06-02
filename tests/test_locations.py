from fastapi import status


def test_get_locations_unauthorized(client):
    response = client.get("/locations/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_locations_empty(auth_client):
    response = auth_client.get("/locations/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_add_and_duplicate_location(auth_client, mocker, test_location):
    mocker.patch(
        "app.weather_service.WeatherFinder.get_weather_by_location_name",
        return_value=test_location,
    )

    response = auth_client.get("/locations/find?location_name=London")
    assert response.status_code == 200
    weather_data = response.json()

    response = auth_client.post("/locations/add", json=weather_data)
    assert response.status_code == status.HTTP_201_CREATED

    response = auth_client.post("/locations/add", json=weather_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]

    response = auth_client.get("/locations/")
    assert len(response.json()) == 1


def test_delete_location(auth_client, test_location_in_db):
    response = auth_client.delete(f"/locations/{test_location_in_db.name_en}")
    assert response.status_code == status.HTTP_200_OK

    response = auth_client.get("/locations/")
    assert len(response.json()) == 0


def test_update_location(
    db_session, auth_client, test_location_in_db, test_location, mocker
):
    time_before = test_location_in_db.weather_updated_at

    mocker.patch(
        "app.weather_service.WeatherFinder.get_weather_by_location_name",
        return_value=test_location,
    )

    response = auth_client.put("/locations/London")
    assert response.status_code == status.HTTP_200_OK

    db_session.refresh(test_location_in_db)

    assert test_location_in_db.weather_updated_at != time_before
