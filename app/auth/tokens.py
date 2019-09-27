from flask import jsonify
from flask import g

from app.auth import bp
from app.auth.auth import basic_auth


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({"token": token})


@bp.route('/tokens', methods=['DELETE'])
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204