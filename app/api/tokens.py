from flask import g, jsonify

from app import csrf, db
from app.api import bp
from app.api.auth import basic_auth, token_auth


@csrf.exempt
@bp.route("/tokens", methods=["POST"])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({"token": token})


@csrf.exempt
@bp.route("/tokens", methods=["DELETE"])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return "", 204
