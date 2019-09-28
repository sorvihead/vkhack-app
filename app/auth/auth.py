from flask import g

from app import basic_auth

from app.models import User
from app.errors.errors import error_response


@basic_auth.verify_password
def verify_password(username, password):
    print(username)
    user = User.query.filter_by(email=username).first()
    print(username, password, user.check_password(password))
    if not user:
        return False

    g.current_user = user
    print(g.current_user)

    return user.check_password(password)


@basic_auth.error_handler
def basic_auth_error():
    return error_response(401)
