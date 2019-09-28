from app import db
from app import basic_auth

from app.models import User
from app.models import Organization
from app.models import Event

from app.schemas import UserSchema
from app.schemas import OrganizationSchema
from app.schemas import EventSchema

from app.main import bp
from app.errors.errors import error_response

from flask import request
from flask import jsonify
from flask import url_for

from sqlalchemy.exc import ArgumentError, IntegrityError

user_schema = UserSchema()
users_schema = UserSchema(many=True)
org_schema = OrganizationSchema()
orgs_schema = OrganizationSchema(many=True)
event_schema = OrganizationSchema()
events_schema = OrganizationSchema(many=True)


#  USERS
@bp.route('/users/get/<int:pk>', methods=['GET'])
@basic_auth.login_required
def get_profile(pk):
    user = User.query.get_or_404(pk)
    return user_schema.jsonify(user)


@bp.route('/users/edit/<int:pk>', methods=['PUT'])
@basic_auth.login_required
def edit_user(pk):
    user = User.query.get_or_404(pk)
    data = request.get_json()
    email_duplicate = User.query.filter_by(email=data.get('email')).first()
    if email_duplicate and email_duplicate != user:
        return jsonify({"error": "email must be unique"})
    for key in data:
        setattr(user, key, data[key])
    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user)
    


#  ORGANIZATIONS
@bp.route('/organizations/get/<int:pk>', methods=['GET'])
@basic_auth.login_required
def get_organization(pk):
    return 'ok' # to dict


@bp.route('/organizations/edit/<int:pk>', methods=['PUT'])
@basic_auth.login_required
def edit_organization(pk):
    return 'ok'


@bp.route('/organizations/get', methods=['GET'])
@basic_auth.login_required
def get_organizations():
    return 'ok'


#  EVENTS
@bp.route('/events/get', methods=['GET'])
@basic_auth.login_required
def get_event_from_org():
    oid = request.json.get('oid', '', type=int)
    if not oid:
        oid = 1
    org = Organization.query.get_or_404(oid)
    return 'ok'  # to dict


@bp.route('/events/get/<int:pk>')
@basic_auth.login_required
def get_event(pk):
    return 'ok' # to dict