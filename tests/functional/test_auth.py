from flask import url_for


def test_login_page(client):
    """
    GIVEN a Flask application
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = client.get(url_for("auth.login"))
    assert response.status_code == 200
