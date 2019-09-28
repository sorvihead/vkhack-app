from app import db

from app.errors import bp

from flask import request
from flask import jsonify

from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@bp.errorhandler(400)
def bad_request(error):
    return error_response(400)


@bp.errorhandler(404)
def not_found_error(error):
    return error_response(404)


@bp.errorhandler(500)
def internal_server_error(error):
    return error_response(500)