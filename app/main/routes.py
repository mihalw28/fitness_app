from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, \
    current_app, jsonify, g
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, ActivityForm, SignUpForm
from app.models import User, Activity, Train
from app.main import bp
from selenium import webdriver
import time
from config import Config

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = ActivityForm()
    if form.validate_on_submit():
        activity = Activity(activ_body=form.activity.data, author=current_user)
        db.session.add(activity)
        db.session.commit()
        flash('Your activity is posted now!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    activities = current_user.followed_activities().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('main.index', page=activities.prev_num) \
        if activities.has_prev else None
    return render_template('index.html', title='Home Page', form=form,
                           activities=activities.items, next_url=next_url, prev_url=prev_url)
'''
@bp.route('/signup')
@login_required
def signup():
    form2 = SignUpForm()
    if form2.validate_on_submit():
        url = 'https://fabrykaformy.perfectgym.pl/ClientPortal2/#/Login'
        driver = webdriver.Chrome('/Users/micha/Documents/GitHub/fitness_app/chromedriver')
        driver.get(url)
        time.sleep(3) #obligatory for waiting to load page
        driver.find_element_by_xpath("//div/input[@name='Login']").send_keys(current_app.config['GYM_USER_NAME'])
        driver.find_element_by_xpath("//div/input[@name='Password']").send_keys(current_app.config['GYM_USER_PASSWORD'])
        time.sleep(2) # just to see results
        driver.find_element_by_class_name('auth-form-actions').click()
        # next page
        time.sleep(6)
        calendar_url = 'https://fabrykaformy.perfectgym.pl/ClientPortal2/#/Classes/22/List'
        driver.get(calendar_url)
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
        workout_index = list_all.index("pilates")    
        web_index = workout_index + 2 # from analysis of gym website
        web_index = str(web_index)
        driver.find_element_by_css_selector(".cp-class-container > div:nth-of-type(2) > div:nth-of-type(" + web_index + ") .class-item-actions").click()
        time.sleep(4)
        driver.find_element_by_css_selector(".is-booked .class-item-actions").click()
        
        training = Train(your_trainig=form2.training.data, author=current_user)
        db.session.add(training)
        db.session.commit()
        flash('We are trying to sign up you for trainig!')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    activities = current_user.followed_activities().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('main.index', page=activities.prev_num) \
        if activities.has_prev else None
    return render_template('.index.html', title='Signup', activities=activities.items, form2=form2,
                            next_url=next_url, prev_url=prev_url)
'''
@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    activities = Activity.query.order_by(Activity.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('main.explore', page=activities.prev_num) \
        if activities.has_prev else None
    return render_template("index.html", title="Explore", activities=activities.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    activities = user.activities.order_by(Activity.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('main.user', username=user.username, page=activities.prev_num) \
        if activities.has_prev else None
    return render_template('user.html', user=user, activities=activities.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.club_name = form.club_name.data
        current_user.classes = form.classes.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        current_user.club_name = form.club_name.data
        current_user.classes = form.classes.data
    return render_template('edit_profile.html', title='Edit Profile', form=form)