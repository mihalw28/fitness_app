def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the name
    """
    assert new_user.username == "Mark"
    assert new_user.password_hash != "DoItNow"
    assert new_user.email == "mark@orni.com"
    assert new_user.cell_number == "123123123"
    assert new_user.club_site_login == "salon"
    assert new_user.club_name == "Kino"
    assert new_user.club_no == 1


def test_password_hashing(new_user):
    """
    GIVEN an existing user
    WHEN the password for the user is set
    THEN check the password is stored correctly
    """
    new_user.set_password("kij")
    assert new_user.password_hash != "gnom"
    assert not new_user.check_password("jik")
    assert not new_user.check_password("kijj")
    assert new_user.check_password("kij")


def test_user_id(new_user):
    """
    GIVEN an existing user
    WHEN the ID of the user is defined to a value
    THEN check the user ID returns an integer
    """
    new_user.id = 123
    assert isinstance(new_user.id, int)
    assert not isinstance(new_user.id, str)
    assert new_user.id == 123


def test_avatar(new_user):
    """
    GIVEN an existing user
    WHEN the user's avatar is set based on email
    THEN check the avatar adress
    """
    assert (
        new_user.avatar(128)
        == "https://www.gravatar.com/avatar/38dd64125c5c68fc6b296a90ef3c1f54?d=retro&s=128"
    )
