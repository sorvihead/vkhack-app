from app import db
from app import ma

from app.models import Chat
from app.models import User
from app.schemas import UserSchema
from app.schemas import ChatSchema
from app.schemas import MessageSchema
from app.chat.helpers import get_sorted_chats

from app.chat import bp

from flask import jsonify
from flask import request
from flask import url_for

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import ArgumentError

import random
import requests


chat_schema = ChatSchema()
chats_schema = ChatSchema(many=True)
msg_schema = MessageSchema()
msgs_schema = MessageSchema(many=True) 


@bp.route('/add', methods=["POST"])
def add_chat():
    if request.content_type == "application/json":
        chat_info = request.json
        errors = chat_schema.validate(chat_info)
        if errors:
            return jsonify(errors), 400
        try:
            chat = chat_schema.load(chat_info)
            db.session.add(chat)
            db.session.commit()
            return jsonify(chat.id)
        except ArgumentError as err:
            return jsonify({"error": [error for error in err.args]}), 400


@bp.route('/get', methods=["POST"])
def get_chats():
    if request.content_type == 'application/json':
        user_info = request.json
        if not user_info.get('user'):
            return jsonify({"error": "missing field user"}), 400
        errors = user_schema.validate(user_info, partial=True)
        if errors:
            return jsonify(errors), 400
        user = User.query.get(user_info.get('user'))
        if not user:
            return jsonify({"error": f"user is not found"}), 404
        chats = get_sorted_chats(user.chats)
        return chats_schema.jsonify(chats)


@bp.route('/message', methods=['POST'])
def add_message():
    data = request.get_json()
    errors = msg_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    msg = msg_schema.load(data)
    z= 14
    c = random.random()*100, random.random()*100
    app_id = 'bPRwtLoyZ1btWqVWgEyn'
    app_code = '_L1NIuHfrB9fdFslixTagA'
    url = f'https://image.maps.api.here.com/mia/1.6/mapview?c={c[0]}%2C{c[1]}&z={z}&app_id={app_id}&app_code={app_code}'
    r = requests.get(url).content
    msg.attachment = r
    db.session.add(msg)
    db.session.commit()
    return msg_schema.jsonify(msg)
