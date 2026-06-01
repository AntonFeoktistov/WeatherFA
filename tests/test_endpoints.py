from fastapi import status


def test_get_index(client):
    response = client.get("/")
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "Hello" in data.get("message")
