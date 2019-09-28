from app import db

from app.auth import bp
from app.errors.errors import bad_request

from app.models import User

from flask import request
from flask import url_for
from flask import jsonify

from app.schemas import UserSchema

user_schema = UserSchema()


@bp.route('users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
 
    if 'name' not in data or 'email' not in data or 'password' not in data or 'surname' not in data:
        return bad_request('must include name, email, surname and password fields')

    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')

    password = data['password']

    data = {elem: data[elem] for elem in data if elem != 'password'}   

    user = user_schema.load(data)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return user_schema.jsonify(user)


        
        