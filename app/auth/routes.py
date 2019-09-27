from app import db

from app.auth import bp
from app.auth.errors import bad_request

from app.models import User

from flask import request
from flask import url_for
from flask import jsonify


@bp.route('users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    
    if User.query.filter_by(username=data['username'].first()):
        return bad_request('please use a different name')
    
    if User.query.filter_by(email=data['email'].first()):
        return bad_request('please use a different email address')

    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('auth.get_user', id=user.id)
    return response


        
        