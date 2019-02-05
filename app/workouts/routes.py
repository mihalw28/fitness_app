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
from app.workouts.forms import SignUpForTraining

@bp.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    form = SignUpForTraining(current_user.username)
    if form.validate_on_submit():
        #LOGIN_URL = 'https://fabrykaformy.perfectgym.pl/ClientPortal2/#/Login'
        driver = webdriver.Chrome('/Users/micha/Documents/GitHub/fitness_app/chromedriver')
        driver.get(current_app.config['GYM_LOGIN_URL'])
        time.sleep(3) #obligatory for waiting to load page
        current_user.club_site_login = form.user_club_login.data
        current_user.club_site_password = form.user_club_password.data
        driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(current_app.config['GYM_USER_NAME'])
        driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(current_app.config['GYM_USER_PASSWORD'])
        time.sleep(2) # just to see results no need in headless mode
        driver.find_element_by_class_name('auth-form-actions').click()
        time.sleep(6) # next page waiting

        #######################################################################
        ############ PROBLEM HERE | #####################################
        ############# below #######################################
        
        current_user.club_no = form.user_club_number.data
        cucn = request.args.get('club_no', type=int)
        #u = User(club_no = str(cucn))
        list_url = current_app.config['GYM_LIST_CLASSES'] + str(cucn) + '/List'
        #list_url = 'https://fabrykaformy.perfectgym.pl/ClientPortal2/#/Classes/22/List'
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
        current_user.classes = form.training.data
        workout_index = 2#list_all.index("current_user.classes")    
        web_index = workout_index + 2 # from analysis of gym website
        web_index = str(web_index)
        driver.find_element_by_css_selector(".cp-class-container > div:nth-of-type(2) > div:nth-of-type(" + web_index + ") .class-item-actions").click()
        time.sleep(4)
        driver.find_element_by_css_selector(".is-booked .class-item-actions").click()
        #gym_activity = Train(your_trainig=form.gym_activity.data, author=current_user)
        #db.session.add(gym_activity)
        #db.session.commit()
        #flash('We are trying to sign up you for trainig!')
        #return redirect(url_for('main.index'))
        flash('Może się uda!')
    return render_template('workouts/signup.html', title='Signup', form=form)
