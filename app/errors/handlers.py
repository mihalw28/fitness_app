from flask import render_template, request

from app import db
from app.api.errors import error_response as api_error_response
from app.errors import bp


def wants_json_response():
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return (
        best == "application/json"
        and request.accept_mimetypes[best] >= request.accept_mimetypes["text/html"]
    )


@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template("errors/500.html"), 500


@bp.app_errorhandler(405)
def method_not_allowed_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template("errors/405.html"), 405