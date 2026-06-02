from fastapi import status


def test_weather_service(client):
    response = client.get("/locations/find", params={"location_name": "London"})
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data.get("location").get("name_en") == "London"
    assert data.get("description")
    assert data.get("temperature")
    assert data.get("wind_speed")


def test_weather_service_not_correct_request(client):
    response = client.get("/locations/find", params={"location_name": "fhusvidvoidv"})
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not data.get("location")
    assert not data.get("description")
    assert not data.get("temperature")
    assert not data.get("wind_speed")
