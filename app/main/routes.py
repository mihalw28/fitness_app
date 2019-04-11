from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, \
    current_app  # , jsonify, g
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
# from app.workouts.forms import SignUpForTrainingForm
from app.models import User, Train
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    activities = current_user.followed_trainings().paginate(
        page, current_app.config['ACTIVITIES_PER_PAGE'], False)
    next_url = url_for('main.index', page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('main.index', page=activities.prev_num) \
        if activities.has_prev else None
    return render_template('index.html', title='Home Page',
                           activities=activities.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    activities = Train.query.order_by(Train.timestamp.desc()).paginate(
        page, current_app.config['ACTIVITIES_PER_PAGE'], False)
    next_url = url_for('main.explore', page=activities.next_num) \
        if activities.has_next else None
    prev_url = url_for('main.explore', page=activities.prev_num) \
        if activities.has_prev else None
    return render_template("index.html", title="Przeglądaj",
                           activities=activities.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    activities = user.trainings.order_by(Train.timestamp.desc()).paginate(
        page, current_app.config['ACTIVITIES_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=activities.
                       next_num) if activities.has_next else None
    prev_url = url_for('main.user', username=user.username, page=activities.
                       prev_num) if activities.has_prev else None
    return render_template('user.html', user=user, activities=activities.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.cell_number)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.club_name = form.club_name.data
        current_user.classes = form.classes.data
        current_user.cell_number = form.cell_number.data
        db.session.commit()
        flash('Zmiany w Twoim profilu zostały zapisane.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        current_user.club_name = form.club_name.data
        current_user.classes = form.classes.data
        form.cell_number.data = current_user.cell_number
    return render_template('edit_profile.html', title='Edytuj profil',
                           form=form)
