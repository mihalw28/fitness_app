from app.api import bp
from flask import jsonify, request, url_for, g, abort
from app.models import User, Train
from app import db
from app.api.errors import bad_request
from app.api.auth import token_auth
from app import csrf


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users/<int:id>/trainings', methods=['GET'])
@token_auth.login_required
def get_user_trainings(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Train.to_collection_dict(user.followed_trainings(), page, per_page,
                                   'api.get_user_trainings', id=id)
    return jsonify(data)

# Below route is unnecessary in production, but was made for practise
@csrf.exempt
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('Prosze podać nazwę użytkownika, email i hasło')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Porszę użyć innej nazwy użytkownika')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Prosze użyć innego adresu email')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@csrf.exempt
@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if g.current_user.id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('Proszę wybrać inną nazwę użytkownika')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('Proszę użyć innego adresu email')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())
