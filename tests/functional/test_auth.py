from flask import redirect, url_for

from app.models import User


def test_login_page(client):
    """
    GIVEN a Flask application
    WHEN the '/auth/login' page is requested (GET)
    THEN check the response is valid
    """
    response = client.get(url_for("auth.login"))
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert not b"Login" in response.data
    assert "Hasło" in response.get_data(as_text=True)


def test_invalid_method_on_logout(client):
    """
    GIVEN a Flask application
    WHEN the "/auth/logout" page is posted
    THEN check the method is invalid 
    """
    response = client.post(url_for("auth.logout"), follow_redirects=True)
    assert response.status_code == 405


def test_valid_login_logout(client):
    """
    GIVEN a Flask application
    WHEN the "/auth/login" page is posted to (POST)
    THEN check responses
    """
    response = client.post(
        url_for("auth.login"),
        data=dict(username="micha", password="micha"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Czołem micha!" in response.get_data(as_text=True)
    assert "Starsze aktywności" in response.get_data(as_text=True)
    assert "Wyloguj się" in response.get_data(as_text=True)
    assert "Profil" in response.get_data(as_text=True)

    """
    GIVEN a Flask application
    WHEN the "/logout" page is requested
    THEN check response is valid
    """
    response = client.get(url_for("auth.logout"), follow_redirects=True)
    assert response.status_code == 200
    assert "Zaloguj się" in response.get_data(as_text=True)
    assert "Hasło" in response.get_data(as_text=True)
    assert "Nazwa użytkownika" in response.get_data(as_text=True)
    assert "Nie masz jeszcze konta?" in response.get_data(as_text=True)


def test_invalid_login_logout(client):
    """
    GIVEN a flask application
    WHEN the "/login" page is posted with invalid credentials
    THEN check error message returned
    """
    response = client.post(
        url_for("auth.login"),
        data=dict(username="micha", password="achim"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Niepoprawna nazwa uzytkownika lub hasło" in response.get_data(as_text=True)
    assert "Zaloguj się" in response.get_data(as_text=True)
    assert "Hasło" in response.get_data(as_text=True)


def test_valid_registration(client, new_user):
    """
    GIVEN a flask application
    WHEN the "/auth/register" page is posted
    THEN check the response is valid and user is able to log in
    """
    # form = RegistrationForm(formdata=None, obj=new_user)
    response = client.post(
        url_for("auth.register"),
        data=dict(
            username=new_user.username,
            email=new_user.email,
            cell_number=new_user.cell_number,
            club_site_login=new_user.club_site_login,
            club_site_password=new_user.club_site_password,
            password="nowe",
            password2="nowe",
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Gratulacje, pomyślnie ukończyłaś/eś proces rejestracji." in response.get_data(
        as_text=True
    )
    assert "Zaloguj się" in response.get_data(as_text=True)
    assert "Hasło" in response.get_data(as_text=True)

    """
    GIVEN a flask application
    WHEN the "/auth/login" page is requested
    THEN check if possible to log in with already registered user credentials
    """
    response = client.post(
        url_for("auth.login"),
        data=dict(username=new_user.username, password="nowe"),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Wyloguj się" in response.get_data(as_text=True)


def test_invalid_registration(client, new_user):
    """
    GIVEN a flask application
    WHEN the "/auth/register" page is posted
    THEN check the response is valid and user is able to log in
    """
    response = client.post(
        url_for("auth.register"),
        data=dict(
            username=new_user.username,
            email=new_user.email,
            cell_number=new_user.cell_number,
            club_site_login=new_user.club_site_login,
            club_site_password=new_user.club_site_password,
            password="nowe",
            password2="nowe",
        ),
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        "Wybrana nazwa użytkownika jest już zajęta."
        or "Podany adres email jest już zajęty"
        or "Prosze wpisać inny numer telefonu."
        or "Wybrana nazwa juz istnieje."
    ) in response.get_data(as_text=True)
