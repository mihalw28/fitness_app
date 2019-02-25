from flask import render_template, flash, redirect, url_for, request, Flask
from app import db
from app.workouts import bp
from flask import current_app
from flask_login import current_user, login_user, login_required
from app.models import User, Train
from selenium import webdriver
import time
from config import Config
from app.workouts.forms import SignUpForTrainingForm, CancelTrainingForm
import dateparser
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from app import csrf
import datetime
import pytz


#headles chrome 
'''Uncomment before deployment'''
#options = webdriver.ChromeOptions()
#options.add_argument('headless')


@bp.route('/signup', methods=['GET', 'POST'])
#@login_required
def signup():
    #form = SignUpForTrainingForm(current_user.username)
    #if form.validate_on_submit():
    users = User.query.all()
    for user in users: 
        driver = webdriver.Chrome('/Users/micha/Documents/GitHub/fitness_app/chromedriver')#, chrome_options=options)
        driver.get(current_app.config['GYM_LOGIN_URL'])
        time.sleep(4) #obligatory for waiting to load page
        driver.find_element_by_xpath("//div/input[@name='Login']") \
            .send_keys(user.club_site_login)
        driver.find_element_by_xpath("//div/input[@name='Password']") \
            .send_keys(user.club_site_password)
        time.sleep(2) # just to see results no need in headless mode
        driver.find_element_by_class_name('auth-form-actions').click()
        time.sleep(6) # next page waiting
        list_url = current_app.config['GYM_LIST_CLASSES'] + str(user.club_name) + '/List'
        driver.get(list_url)
        time.sleep(4)

        # find date string 
        date = driver.find_element_by_css_selector(".cp-class-container > div:nth-of-type(2) \
                                                    .class-list-day-title").text.lower()
        # list all activities in one day 
        list_all = []
        list_all_day_act = driver.find_elements_by_css_selector(".cp-class-container > div:nth-of-type(2) \
                                                                 .calendar-item-name")
        for element in list_all_day_act:
            list_all.append((element.text).lower())
        # list all bookable activities and their start time
        list_bookable = []
        list_all_bookable_act = driver.find_elements_by_css_selector(".cp-class-container > div:nth-of-type(2) \
                                                                      .is-bookable .calendar-item-name")
        for element in list_all_bookable_act:
            list_bookable.append((element.text).lower())
        # list all activities' start time
        list_all_start = []
        list_hours = driver.find_elements_by_css_selector(".cp-class-container > div:nth-of-type(2) \
                                                           .calendar-item-start")
        for element in list_hours:
            list_all_start.append(element.text)

        #combine date & start hour strings, then list parsed
        date_hour = []
        for hour in list_all_start:
            date_hour.append(date + ' ' + hour)

        parsed_dates = []
        for element in date_hour:
            right_format_data = dateparser.parse(element, languages=['pl'])
            parsed_dates.append(right_format_data)

        user_training = user.classes.lower()
        if not user_training in list_bookable:
            flash("Niestety nie możesz się teraz zapisać na swój trening.")
        else:
            # find index of desirable workout and book
            workout_index = list_all.index((user.classes).lower())    
            web_index = str(workout_index + 2) # from gym website
            driver.find_element_by_css_selector(".cp-class-container > div:nth-of-type(2) > div:nth-of-type(" + web_index + ") \
                                                 .class-item-actions").click()
            time.sleep(4) # just for visual check
            training_datetime = parsed_dates[workout_index-1]
            training_activity = Train(your_training=user.classes, training_datetime=training_datetime, 
                                      author=current_user)
            db.session.add(training_activity)
            db.session.commit()
            flash('Jesteś zapisana/y na trening.')
            
            #send sms
            client = Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
            message = client.messages.create(
                body = f'Hej, bierzesz udział w zajęciach {user_training}, które odbędą się {training_datetime}! Potwierdź wysyłając "tak". Jeżeli z jakiegoś powodu \
                        nie weźmiesz udziału odpisz "nie". Jeżeli nie potwierdzisz uczestnictwa do 4 godzin przed rozpoczęciem \
                        zajęć, towja rezerwacja zostanie automatycznie anulowana.',
                from_= '+48732168578',
                to = '+48' + str(user.cell_number)
            )
            print(message.sid)
        return redirect(url_for('main.index'))
    return render_template('workouts/signup.html', title='Signup')#, form=form)


@csrf.exempt # Some errors without this decorator
@bp.route('/sms', methods=['POST', 'GET'])
def sms():
    resp = MessagingResponse()
    from_number = request.values.get('From', None) #need to cut country prefix
    strip_number = from_number[3:]
    body = request.values.get('Body', None)
    user = User.query.filter_by(cell_number=strip_number).first() # find user on cell_number not username
    if "tak" in body.lower():
        Train.query.filter_by(user_id=user.id).order_by(Train.timestamp.desc()).first().acceptance = 'tak'
        db.session.commit()
        resp.message("Dzięki za potwierdzenie. Udanego treningu.")
    elif "nie" in body.lower():
        driver = webdriver.Chrome('/Users/micha/Documents/GitHub/fitness_app/chromedriver')
        driver.get(current_app.config['GYM_LOGIN_URL'])
        time.sleep(3) #obligatory for waiting to load page
        driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(user.club_site_login)
        driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(user.club_site_password)
        time.sleep(2) # just to see results no need in headless mode
        driver.find_element_by_class_name('auth-form-actions').click()
        time.sleep(6) # next page waiting
        list_url = current_app.config['GYM_LIST_CLASSES'] + str(user.club_name) + '/List'
        driver.get(list_url)
        time.sleep(4)
        driver.find_element_by_css_selector(".is-booked .class-item-actions").click()
        time.sleep(1)
        trainings = Train.query.filter_by(user_id=user.id).order_by(Train.timestamp.desc()).first()
        # delete training from user profile
        db.session.delete(trainings)
        db.session.commit()
        resp.message("Rezerwacja treningu z poprzedniej wiadomości odwołana. Miłego dnia.")
    else:
        resp.message(f"Coś źle poszło. Odpisz 'tak' jeżeli potwierdzasz udział lub 'nie' jeżeli odwołujesz rezerwację. Ty napisałaś/eś: {body}.")
    return str(resp)

# cancel training manually from web
@bp.route('/cancel', methods=['GET', 'POST'])
@login_required #- no need to login, this 
def cancel():
    form2 = CancelTrainingForm(current_user.username)
    if form2.validate_on_submit():
        # Make browser headless in future here
        user = User.query.filter_by(username=current_user.username).first() # find user on cell_number not username
        driver = webdriver.Chrome('/Users/micha/Documents/GitHub/fitness_app/chromedriver')#, chrome_options=options)
        driver.get(current_app.config['GYM_LOGIN_URL'])
        time.sleep(3) #obligatory for waiting to load page
        driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(user.club_site_login)
        driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(user.club_site_password)
        time.sleep(2) # just to see results no need in headless mode
        driver.find_element_by_class_name('auth-form-actions').click()
        time.sleep(6) # next page waiting
        list_url = current_app.config['GYM_LIST_CLASSES'] + str(user.club_name) + '/List'
        driver.get(list_url)
        time.sleep(4)
        driver.find_element_by_css_selector(".is-booked .class-item-actions").click()
        time.sleep(1)
        trainings = current_user.followed_trainings().first()
        db.session.delete(trainings)
        db.session.commit()
        flash('Day off. Netflix & chill.')
        return redirect(url_for('main.index'))
    return render_template('workouts/signup.html', title='Cancel', form2=form2)


#unbook all unconfirmed traininges for 4 hours before trainig
@bp.route('/unbook', methods=['GET', 'POST'])
def unbook():
    users = User.query.all()
    for user in users:
        last_training_time = Train.query.filter_by(user_id=user.id).order_by(Train.timestamp.desc()).first().trining_datetime
        is_confirmed = Train.query.filter_by(user_id=user.id).order_by(Train.timestamp.desc()).first().acceptance
        tz = pytz.timezone('Europe/Warsaw')
        warsaw_now = datetime.datetime.now(tz)
        delta_hours = (last_training_time - warsaw_now).seconds / 3600
        if delta_hours <= 4.0:
            if is_confirmed == "no":
                driver = webdriver.Chrome('/Users/micha/Documents/GitHub/fitness_app/chromedriver')#, chrome_options=options)
                driver.get(current_app.config['GYM_LOGIN_URL'])
                time.sleep(3) #obligatory for waiting to load page
                driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(user.club_site_login)
                driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(user.club_site_password)
                time.sleep(2) # just to see results no need in headless mode
                driver.find_element_by_class_name('auth-form-actions').click()
                time.sleep(6) # next page waiting
                list_url = current_app.config['GYM_LIST_CLASSES'] + str(user.club_name) + '/List'
                driver.get(list_url)
                time.sleep(4)
                driver.find_element_by_css_selector(".is-booked .class-item-actions").click()
                time.sleep(1)
                trainings = current_user.followed_trainings().first()
                db.session.delete(trainings)
                db.session.commit()
            else:
                pass
        else:
            pass
