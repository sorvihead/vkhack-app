from app import db
from app import basic_auth

from app.models import User
from app.models import Organization
from app.models import Event
from app.main import bp
from app.errors.errors import error_response

from flask import request
from flask import jsonify
from flask import url_for

from sqlalchemy.exc import ArgumentError, IntegrityError


@bp.route('/users/get/<int:pk>', methods=['GET'])
@basic_auth.login_required
def get_profile(pk):
    return User.query.get_or_404(pk) #  to dict


@bp.route('/users/edit/<int:pk>', methods=['PUT'])
@basic_auth.login_required
def edit_profile(pk):
    print(request.get_json())
    user = User.query.get_or_404(pk)
    data = request.get_json()
    try:
        user.from_dict(data)
    except ArgumentError as err:
        message = err.args[0]
        return error_response(400, message)
    except IntegrityError:
        return error_response(400, 'email must be unique')
    db.session.commit()
    print(user.to_dict())
    return jsonify(user.to_dict())


@bp.route('/organizations/get/<int:pk>', methods=['GET'])
@basic_auth.login_required
def get_organization(pk):
    return Organization.query.get_or_404(pk)  # to dict


@bp.route('/events/get', methods=['GET'])
@basic_auth.login_required
def get_event_from_org():
    oid = request.json.get('oid', '', type=int)
    if not oid:
        oid = 1
    org = Organization.query.get_or_404(oid)
    return [event for event in org.events]  # to dict


@bp.route('/events/get/<int:pk>')
@basic_auth.login_required
def get_event(pk):
    return Event.query.get_or_404(pk)  # to dict