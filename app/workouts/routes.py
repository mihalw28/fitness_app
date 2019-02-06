from flask import render_template, flash, redirect, url_for, request
from app import db
from app.workouts import bp
from flask import current_app
#from app.auth.forms import LoginForm, RegistrationForm,  ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, login_required
from app.models import User, Train
from werkzeug.urls import url_parse
from selenium import webdriver
import time
from config import Config
from app.workouts.forms import SignUpForTrainingForm

@bp.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    form = SignUpForTrainingForm(current_user.username)
    if form.validate_on_submit():
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

        # all activieties in one day
        list_all_day_act = driver.find_elements_by_css_selector(".cp-class-container > div:nth-of-type(2) .calendar-item-name")
        list_all = []
        for workout in list_all_day_act:
            list_all.append((workout.text).lower())
        
        # all bookable activities
        list_all_bookable_act = driver.find_elements_by_css_selector(".cp-class-container > div:nth-of-type(2) .is-bookable .calendar-item-name")
        list_bookable = []
        for workout in list_all_bookable_act:
            list_bookable.append((workout.text).lower())
        
        # find index of desirable workout in all workouts
        workout_index = list_all.index((user.classes).lower())    
        web_index = str(workout_index + 2) # from gym website
        #web_index = str(web_index)
        driver.find_element_by_css_selector(".cp-class-container > div:nth-of-type(2) > div:nth-of-type(" + web_index + ") .class-item-actions").click()
        time.sleep(4) # just for visual check

        # Unbook class - need to extend this line
        driver.find_element_by_css_selector(".is-booked .class-item-actions").click()
        training_activity = Train(your_training = user.classes, author=current_user) #misspelling
        db.session.add(training_activity)
        db.session.commit()
        flash('We are trying to sign up you for trainig!')
        return redirect(url_for('main.index'))
    return render_template('workouts/signup.html', title='Signup', form=form)
