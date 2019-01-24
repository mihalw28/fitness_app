from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ActivityForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Activity
from werkzeug.urls import url_parse
from datetime import datetime
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = ActivityForm()
    if form.validate_on_submit():
        activity = Activity(activ_body=form.activity.data, author=current_user)
        db.session.add(activity)
        db.session.commit()
        flash('Your activity is posted now!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    activities = current_user.followed_activities().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('index', page=activities.prev_num) \
        if activities.has_prev else None
    return render_template('index.html', title='Home Page', form=form, 
                           activities=activities.items, next_url=next_url,
                           prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    activities = Activity.query.order_by(Activity.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('explore', page=activities.prev_num) \
        if activities.has_prev else None
    return render_template("index.html", title="Explore", activities=activities.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '': #security issues
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    cell_number=form.cell_number.data, 
                    club_site_login=form.club_site_login.data,
                    club_site_password=form.club_site_password.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email. Instructions are waiting for you there.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    activities = user.activities.order_by(Activity.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('user', username=user.username, page=activities.prev_num) \
        if activities.has_prev else None
    return render_template('user.html', user=user, activities=activities.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.yoga = form.yoga.data
        current_user.bodypump = form.bodypump.data
        current_user.calistenics = form.calistenics.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

