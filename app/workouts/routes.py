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


@bp.route('/signup', methods=['GET', 'POST'])
#@login_required
def signup():
    form = SignUpForTrainingForm(current_user.username)
    if form.validate_on_submit():
        # Make browser headless in future here
        user = User.query.filter_by(username=current_user.username).first()
        driver = webdriver.Chrome('/Users/micha/Documents/GitHub/fitness_app/chromedriver')
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
            flash("Your training is not bookable now.")
        else:
            # find index of desirable workout and book
            workout_index = list_all.index((user.classes).lower())    
            web_index = str(workout_index + 2) # from gym website
            driver.find_element_by_css_selector(".cp-class-container > div:nth-of-type(2) > div:nth-of-type(" + web_index + ") \
                                                 .class-item-actions").click()
            time.sleep(4) # just for visual check
            training_datetime = parsed_dates[workout_index-1]
            training_activity = Train(your_training = user.classes, training_datetime=training_datetime, 
                                      author=current_user)
            db.session.add(training_activity)
            db.session.commit()
            flash('We are trying to sign up you for trainig!')
            
            #send sms
            client = Client(current_app.config['TWILIO_ACCOUNT_SID'], current_app.config['TWILIO_AUTH_TOKEN'])
            message = client.messages.create(
                body = 'Świtenie, jesteś zapisany na zajęcia!',
                from_= '+48732168578',
                to = '+' + str(user.cell_number)
            )
            print(message.sid)
        return redirect(url_for('main.index'))
    return render_template('workouts/signup.html', title='Signup', form=form)


@bp.route('/cancel', methods=['GET', 'POST'])
@login_required
def cancel():
    #form2 = CancelTrainingForm(current_user.username)
    #if form2.validate_on_submit():
    if 2 == 2:
        # Make browser headless in future here
        user = User.query.filter_by(username=current_user.username).first()
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
        trainings = current_user.followed_trainings().first()
        db.session.delete(trainings)
        db.session.commit()
        flash('Day off. Netflix & chill.')
        return redirect(url_for('main.index'))
    return render_template('workouts/signup.html', title='Cancel')#, form2=form2)

@csrf.exempt # Some errors without this decorator
@bp.route('/sms', methods=['POST', 'GET'])
#@login_required
def sms():
    resp = MessagingResponse()
    #from_number = request.values.get('From', None)
    body = request.values.get('Body', None)
    #number = from_number
    body_strip = body.lower()
    if "tak" in body_strip:
        resp.message("ok. jesteś zapisany")
    elif "nie" in body_strip:
        resp.message("dzisiaj wolne. wypisuję Cie")
        return redirect(url_for('main.cancel'))
    else:
        resp.message("coś się nie udało. Napisz tak lub nie, ty napisałeś: ")
    return str(resp)