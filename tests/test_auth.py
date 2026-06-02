from fastapi import status


def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"name": "newuser", "password1": "pass123", "password2": "pass123"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == "newuser"


def test_register_duplicate_username(client, test_user):
    response = client.post(
        "/auth/register",
        json={"name": "testuser", "password1": "pass123", "password2": "pass123"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_register_passwords_mismatch(client):
    response = client.post(
        "/auth/register",
        json={"name": "newuser", "password1": "pass123", "password2": "pass456"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_register_passwords_no_two_digits(client):
    response = client.post(
        "/auth/register",
        json={"name": "newuser", "password1": "pass3", "password2": "pass3"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "2 цифры" in response.json()["detail"]


def test_register_passwords_no_two_latin_letters(client):
    response = client.post(
        "/auth/register",
        json={"name": "newuser", "password1": "p33", "password2": "p33"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "2 латинские буквы" in response.json()["detail"]


def test_login_success(client, test_user):
    response = client.post(
        "/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login", json={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
