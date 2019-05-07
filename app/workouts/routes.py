import datetime
import time

import dateparser
from flask import (Flask, current_app, flash, redirect, request, url_for)
from flask_login import current_user, login_required
from selenium import webdriver
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from app import csrf, db, scheduler
from app.auth.crypting import decrypt_gym_password
from app.models import Train, User
from app.workouts import bp
from app.workouts.forms import CancelTrainingForm


# Sign up
@scheduler.task("cron", id="sign_up_users", hour="*/2")
@bp.route("/signup", methods=["GET", "POST"])
def signup():
    with scheduler.app.test_request_context():
        users = User.query.all()
        for user in users:
            if (user.club_name is not None) and (user.classes is not None):
                club_site_password_plain = decrypt_gym_password(user)
                chrome_options = webdriver.ChromeOptions()
                driver_path = (
                    "/Users/micha/Documents/GitHub/fitness_app/chromedriver"
                )  # local
                chrome_options.add_argument("--window-size=1280x1696")  # docker + local
                chrome_options.add_argument("--disable-dev-shm-usage")
                # chrome_options.add_argument('--headless')  # docker
                # chrome_options.add_argument('--no-sandbox')  # docker
                # chrome_options.add_argument('--disable-gpu')  # docker
                # chrome_options.add_argument('--lang=pl')  # necessary to avoid parsing dates error; docker + local in headless mode
                driver = webdriver.Chrome(
                    chrome_options=chrome_options, executable_path=driver_path
                )  # executable path argument; local executions
                driver.get(current_app.config["GYM_LOGIN_URL"])
                time.sleep(4)  # Need time to load page
                driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(
                    user.club_site_login
                )
                driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(
                    # user.club_site_password
                    club_site_password_plain
                )
                time.sleep(0.5)  # Just to see results no need in headless mode
                driver.find_element_by_class_name("auth-form-actions").click()
                time.sleep(4)  # Next page waiting

                list_url = (
                    current_app.config["GYM_LIST_CLASSES"]
                    + "#/Classes/"
                    + str(user.club_name)
                    + "/List"
                )
                driver.get(list_url)
                time.sleep(3)

                # Find date string
                date = driver.find_element_by_css_selector(
                    ".cp-class-container > div:nth-of-type(2) \
                                                            .class-list-day-title"
                ).text.lower()
                # List all activities in one day
                list_all = []
                list_all_day_act = driver.find_elements_by_css_selector(
                    ".cp-class-container > div:nth-of-type(2) .calendar-item-name"
                )
                for element in list_all_day_act:
                    list_all.append((element.text).lower())
                # List all bookable activities and their start time
                list_bookable = []
                list_all_bookable_act = driver.find_elements_by_css_selector(
                    ".cp-class-container > div:nth-of-type(2) .is-bookable .calendar-item-name"
                )
                for element in list_all_bookable_act:
                    list_bookable.append((element.text).lower())
                # List all activities' start time
                list_all_start = []
                list_hours = driver.find_elements_by_css_selector(
                    ".cp-class-container > div:nth-of-type(2) .calendar-item-start"
                )
                for element in list_hours:
                    list_all_start.append(element.text)

                # Combine date & start hour strings, then list parsed
                date_hour = []
                for hour in list_all_start:
                    date_hour.append(date + " " + hour)
                parsed_dates = []
                for element in date_hour:
                    right_format_data = dateparser.parse(element, languages=["pl"])
                    parsed_dates.append(right_format_data)
                user_training = user.classes.lower()
                if user_training in list_bookable:
                    # Find index of desirable workout and book
                    workout_index = list_all.index((user.classes).lower())
                    web_index = str(workout_index + 2)  # From gym website
                    driver.find_element_by_css_selector(
                        ".cp-class-container > div:nth-of-type(2) > div:nth-of-type("
                        + web_index
                        + ") .class-item-actions"
                    ).click()
                    time.sleep(0.5)
                    training_datetime = parsed_dates[workout_index - 1]
                    training_activity = Train(
                        your_training=user.classes,
                        training_datetime=training_datetime,
                        user_id=user.id,
                    )
                    db.session.add(training_activity)
                    db.session.commit()
                    driver.close()
                    # Send sms
                    # Below body_message is one liner and written in
                    # "bad language" due to gsm coding restrictions
                    body_message = f'Hej, trenujesz {user_training} w dniu {training_datetime}! Zaakceptuj - "tak" lub "nie". Jak nie potwierdzisz uczestnictwa do 4 godzin przed startem treninu, twoja rezerwacja zostanie anulowana.'
                    client = Client(
                        current_app.config["TWILIO_ACCOUNT_SID"],
                        current_app.config["TWILIO_AUTH_TOKEN"],
                    )
                    message = client.messages.create(
                        body=body_message,
                        from_=current_app.config["TWILIO_PHONE_NUMBER"],
                        to="+48" + str(user.cell_number),
                    )
                    print(message.sid)
                else:
                    pass
            else:
                pass
    return


@csrf.exempt  # Some errors without this decorator
@bp.route("/sms", methods=["POST", "GET"])
def sms():
    resp = MessagingResponse()
    from_number = request.values.get("From", None)  # Need to cut country prefix
    strip_number = from_number[3:]
    body = request.values.get("Body", None)
    user = User.query.filter_by(
        cell_number=strip_number
    ).first()  # Find user by cell_number not username
    if "tak" in body.lower():
        Train.query.filter_by(user_id=user.id).order_by(
            Train.timestamp.desc()
        ).first().acceptance = "tak"
        db.session.commit()
        resp.message("Dzieki za potwierdzenie. Udanego treningu.")
    elif "nie" in body.lower():
        chrome_options = webdriver.ChromeOptions()
        # driver_path = "/Users/micha/Documents/GitHub/fitness_app/chromedriver"  # local
        chrome_options.add_argument("--window-size=1280x1696")  # docker + local
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # docker
        chrome_options.add_argument("--no-sandbox")  # docker
        chrome_options.add_argument("--disable-gpu")  # docker
        chrome_options.add_argument(
            "--lang=pl"
        )  # necessary for avoiding parsing dates error; docker + local in headless mode
        driver = webdriver.Chrome(
            chrome_options=chrome_options
        )  # , executable_path=driver_path)  # executable path argument; local executions

        driver.get(current_app.config["GYM_LOGIN_URL"])
        time.sleep(1)  # Need time to load page
        driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(
            user.club_site_login
        )
        driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(
            user.club_site_password
        )
        time.sleep(0.5)  # Just to see results no need in headless mode
        driver.find_element_by_class_name("auth-form-actions").click()
        time.sleep(2)  # Next page waiting

        list_url = (
            current_app.config["GYM_LIST_CLASSES"]
            + "#/Classes/"
            + str(user.club_name)
            + "/List"
        )
        driver.get(list_url)
        time.sleep(1)

        driver.find_element_by_css_selector(".is-booked .class-item-actions").click()
        time.sleep(1)
        trainings = (
            Train.query.filter_by(user_id=user.id)
            .order_by(Train.timestamp.desc())
            .first()
        )

        db.session.delete(trainings)  # Delete training from user profile
        db.session.commit()
        driver.close()
        resp.message(
            "Rezerwacja treningu z poprzedniej wiadomosci odwolana. Milego dnia."
        )
    else:
        resp.message(
            f"Zle poszlo. Odpisz 'tak' jezeli potwierdzasz udzial lub 'nie' jezeli odwolujesz rezerwację. Ty napisalas/es: {body}."
        )
    return str(resp)


# Cancel training manually from web app
@bp.route("/cancel_training", methods=["GET", "POST"])
@login_required
def cancel_training():
    form = CancelTrainingForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            username=current_user.username
        ).first()  # find user by cell_number not username
        driver_path = "/Users/micha/Documents/GitHub/fitness_app/chromedriver"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--window-size=1280x1696")  # docker + local
        chrome_options.add_argument("--disable-dev-shm-usage")  # docker
        # chrome_options.add_argument('--headless')  # docker
        # chrome_options.add_argument('--no-sandbox')  # docker
        # chrome_options.add_argument('--disable-gpu')  # docker
        driver = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=driver_path
        )  # docker
        driver.get(current_app.config["GYM_LOGIN_URL"])
        time.sleep(1)  # Obligatory for waiting to load page
        driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(
            user.club_site_login
        )
        driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(
            user.club_site_password
        )
        time.sleep(0.5)  # Just to see results no need in headless mode
        driver.find_element_by_class_name("auth-form-actions").click()
        time.sleep(2)  # Next page waiting
        list_url = (
            current_app.config["GYM_LIST_CLASSES"]
            + "#/Classes/"
            + str(user.club_name)
            + "/List"
        )
        driver.get(list_url)
        time.sleep(1)
        driver.find_element_by_css_selector(".is-booked .class-item-actions").click()
        time.sleep(1)
        trainings = current_user.followed_trainings().first()
        db.session.delete(trainings)
        db.session.commit()
        driver.close()
        flash("Twój trening został odwołany.")
    return redirect(url_for("main.index"))
    # return render_template('index.html')  # , form=form)


# Unbook all unconfirmed traininges - without user permission
@scheduler.task("cron", id="unbook_classes", minute="5", hour="3-17/2")
@bp.route("/unbook", methods=["GET", "POST"])
def unbook():
    with scheduler.app.test_request_context():
        users = User.query.all()
        for user in users:
            last_training_time = (
                Train.query.filter_by(user_id=user.id)
                .order_by(Train.timestamp.desc())
                .first()
                .training_datetime
            )
            is_confirmed = (
                Train.query.filter_by(user_id=user.id)
                .order_by(Train.timestamp.desc())
                .first()
                .acceptance
            )
            delta_hours = (last_training_time - datetime.datetime.now()).seconds / 3600
            if delta_hours <= 4.0:
                if is_confirmed == "nie":
                    driver_path = (
                        "/Users/micha/Documents/GitHub/fitness_app/chromedriver"
                    )  # local
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument(
                        "--window-size=1280x1696"
                    )  # docker + local
                    chrome_options.add_argument("--disable-dev-shm-usage")  # docker
                    # chrome_options.add_argument('--headless')  # docker
                    # chrome_options.add_argument('--no-sandbox')  # docker
                    # chrome_options.add_argument('--disable-gpu')  # docker
                    driver = webdriver.Chrome(
                        chrome_options=chrome_options, executable_path=driver_path
                    )  # docker
                    driver.get(current_app.config["GYM_LOGIN_URL"])
                    time.sleep(1)  # Obligatory for waiting to load page
                    driver.find_element_by_xpath(
                        "//div/input[@name='Login']"
                    ).send_keys(user.club_site_login)
                    driver.find_element_by_xpath(
                        "//div/input[@name='Password']"
                    ).send_keys(user.club_site_password)
                    time.sleep(0.5)  # Just to see results no need in headless mode
                    driver.find_element_by_class_name("auth-form-actions").click()
                    time.sleep(2)  # Next page waiting
                    list_url = (
                        current_app.config["GYM_LIST_CLASSES"]
                        + "#/Classes/"
                        + str(user.club_name)
                        + "/List"
                    )
                    driver.get(list_url)
                    time.sleep(1)
                    driver.find_element_by_css_selector(
                        ".is-booked .class-item-actions"
                    ).click()
                    time.sleep(1)
                    trainings = current_user.followed_trainings().first()
                    db.session.delete(trainings)
                    db.session.commit()
                    return redirect(url_for("main.index"))
            else:
                pass
    return
