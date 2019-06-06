from flask import abort, g, jsonify, request, url_for

from app import csrf, db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.models import Train, User


@bp.route("/users/<int:id>", methods=["GET"])
@token_auth.login_required
def get_user(id):
    """This route gets user with given id."""
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route("/users", methods=["GET"])
@token_auth.login_required
def get_users():
    """This route lists all users."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, "api.get_users")
    return jsonify(data)


@bp.route("/users/<int:id>/trainings", methods=["GET"])
@token_auth.login_required
def get_user_trainings(id):
    """This route lists all trainings of single user."""
    user = User.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    data = Train.to_collection_dict(
        user.followed_trainings(), page, per_page, "api.get_user_trainings", id=id
    )
    return jsonify(data)


@csrf.exempt
@bp.route("/users", methods=["POST"])
def create_user():
    """This route register new users."""
    data = request.get_json() or {}
    for field in [
        "username",
        "email",
        "password",
        "cell_number",
        "club_site_login",
        "club_site_password",
    ]:
        if field not in data:
            return bad_request(
                "Prosze podać nazwę użytkownika, email, hasło, telefon i dane do logowania na stronie klubu."
            )
    if User.query.filter_by(username=data["username"]).first():
        return bad_request("Porszę użyć innej nazwy użytkownika")
    if User.query.filter_by(email=data["email"]).first():
        return bad_request("Proszę użyć innego adresu email")
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for("api.get_user", id=user.id)
    return response


@csrf.exempt
@bp.route("/users/<int:id>", methods=["PUT"])
@token_auth.login_required
def update_user(id):
    """This API route modify an existing user."""
    if g.current_user.id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if (
        "username" in data
        and data["username"] != user.username
        and User.query.filter_by(username=data["username"]).first()
    ):
        return bad_request("Proszę wybrać inną nazwę użytkownika")
    if (
        "email" in data
        and data["email"] != user.email
        and User.query.filter_by(email=data["email"]).first()
    ):
        return bad_request("Proszę użyć innego adresu email")
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())
