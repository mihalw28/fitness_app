import datetime
import time

import dateparser
from flask import Flask, current_app, flash, redirect, request, url_for
from flask_login import current_user, login_required
from selenium import webdriver
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from app import csrf, db, scheduler
from app.auth.crypting import decrypt_gym_password
from app.models import Train, User
from app.workouts import bp
from app.workouts.forms import CancelTrainingForm


# Scheduled every two hours.
@scheduler.task("cron", id="sign_up_users", hour="*/2")
@bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    This routes automatically signs up users for their trainings.
    """
    with scheduler.app.test_request_context():
        users = User.query.all()
        for user in users:
            if (user.club_name is not None) and (user.classes is not None):
                arg_list = local_options()  # local for now
                driver = get_driver(arg_list)
                log_user(user, driver)
                today = datetime.date.today()
                tommorow_date = today + datetime.timedelta(days=1)
                tommorow = tommorow_date.strftime("%Y-%m-%d")
                list_url = create_url(user, tommorow)
                driver.get(list_url)
                time.sleep(3)

                # List all activities in one day
                list_all_day_act = driver.find_elements_by_css_selector(
                    ".cp-class-list .cp-class-list-day-col .calendar-item-name"
                )
                list_all = [element.text.lower() for element in list_all_day_act]

                # List all bookable activities and their start time
                list_all_bookable_act = driver.find_elements_by_css_selector(
                    ".cp-class-list .cp-class-list-day-col .is-bookable .calendar-item-name"
                )
                list_bookable = [
                    element.text.lower() for element in list_all_bookable_act
                ]

                # List all activities' start time
                list_hours = driver.find_elements_by_css_selector(
                    ".cp-class-list .cp-class-list-day-col .is-bookable .calendar-item-start"
                )
                list_all_start_time = [element.text for element in list_hours]

                # Combine date & start hour strings, then list parsed
                date_hour = [(tommorow + " " + hour) for hour in list_all_start_time]

                # Parse dates
                parsed_dates = [
                    dateparser.parse(element, language=["pl"]) for element in date_hour
                ]

                user_training = user.classes.lower()
                if user_training in list_bookable:
                    # Find index of desirable workout and book

                    """
                    TO DO: change below part -> gym site's been changed recently
                    and this won't work any longer.
                    """
                    workout_index = list_all.index((user.classes).lower())
                    web_index = str(workout_index + 2)  # From gym website
                    driver.find_element_by_css_selector(
                        ".cp-class-container > div:nth-of-type(2) > div:nth-of-type("
                        + web_index
                        + ") .class-item-actions"
                    ).click()
                    time.sleep(0.5)
                    """
                    End of TO DO
                    """

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
                    # "bad formatting" due to gsm coding restrictions
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
                    pass  # sth here in near future
            else:
                pass  # like above
    return


@csrf.exempt
@bp.route("/sms", methods=["POST", "GET"])
def sms():
    """
    This route makes requests based on incoming smses from users. It responds with
    greetings, if user accepts workout or unbooks training if user refuses to take part
    in. 
    """
    resp = MessagingResponse()
    from_number = request.values.get("From", None)  # Need to cut country prefix
    strip_number = from_number[3:]
    body = request.values.get("Body", None)
    user = User.query.filter_by(cell_number=strip_number).first()

    if "tak" in body.lower():
        Train.query.filter_by(user_id=user.id).order_by(
            Train.timestamp.desc()
        ).first().acceptance = "tak"
        db.session.commit()
        resp.message("Dzieki za potwierdzenie. Udanego treningu.")
    elif "nie" in body.lower():
        arg_list = local_options()
        driver = get_driver(arg_list)
        log_user(user, driver)

        date = datetime.date.today()
        list_url = create_url(user, date)
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
    """
    This route sends request to server to cancel user's booked training. It can be
    invoking only manually. No method calls this route.
    """
    form = CancelTrainingForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            username=current_user.username
        ).first()  # Find user by cell_number.
        arg_list = local_options()
        driver = get_driver(arg_list)
        log_user(user, driver)
        date = datetime.date.today()
        list_url = create_url(user, date)
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


# Scheduled every 2 hours.
@scheduler.task("cron", id="unbook_classes", minute="5", hour="3-17/2")
@bp.route("/unbook", methods=["GET", "POST"])
def unbook():
    """
    This route unbooks all unconfirmed training classes, which haven't been confirmed by
    the user 4 hours before particular training starts. 
    """
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
                    arg_list = local_options()
                    driver = get_driver(arg_list)
                    log_user(user, driver)
                    today = datetime.date.today()
                    today_str = today.strftime("%Y-%m-%d")
                    list_url = create_url(user, today_str)
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
    return


def log_user(user, driver):
    """
    "This method logs users to gym site.
    """
    driver.get(current_app.config["GYM_LOGIN_URL"])
    time.sleep(4)
    driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(
        user.club_site_login
    )
    driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(
        decrypt_gym_password(user)
    )
    time.sleep(0.5)
    driver.find_element_by_class_name("auth-form-actions").click()
    time.sleep(4)
    return


def local_options(webdriver):
    """
    This method adds options to webriver and uses it as chrome_options working in local
    environment. It also returns list with chrome_options and driver_path as arguments.
    """
    chrome_options = webdriver.ChromeOptions()
    driver_path = "/Users/micha/Documents/GitHub/fitness_app/chromedriver"
    chrome_options.add_argument("--window-size=1280x1696")
    chrome_options.add_argument("--disable-dev-shm-usage")
    arg_list = [chrome_options, driver_path]
    return arg_list


def docker_options(webdriver):
    """
    This method adds options to webriver and uses it as chrome_options working in docker
    container. It also returns list with chrome_options as an only argument.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1280x1696")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--lang=pl")
    arg_list = [chrome_options]
    return arg_list


def get_driver(arg_list):
    """
    This method creates a driver object depending on docker_options() or local_options()
    fnction.
    """
    try:
        driver = webdriver.Chrome(options=arg_list[0], executable_path=arg_list[1])
    except IndexError:
        driver = webdriver.Chrome(options=arg_list[0])
    return driver


def create_url(user, date):
    """
    This method creates peronalized url for every user.
    Depending on data argument app requests for today's or tommorow's
    calendar.
    """
    list_url = (
        current_app.config["GYM_LIST_CLASSES"]
        + "#/Classes/"
        + str(user.club_name)
        + "/List"
        + "?date="
        + date
        + "T00:00:00"
    )
    return list_url
