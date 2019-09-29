from app import db

from sqlalchemy import event

from sqlalchemy.exc import ArgumentError

from flask import current_app
from flask import url_for

from datetime import datetime
from datetime import date
from datetime import timedelta

from hashlib import md5

from sqlalchemy.exc import ArgumentError

from time import time

from werkzeug.security import generate_password_hash, check_password_hash

import base64
import os
import uuid

volounteers = db.Table(
    'volounteers', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'))
)

participants = db.Table(
    'participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

admins_event = db.Table(
    'admins-event',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

admins_org = db.Table(
    'admins-org',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'))
)


class AuthMixin(object):
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class User(AuthMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), index=True)
    surname = db.Column(db.String(50), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(500))
    bdate = db.Column(db.String(50), index=True)
    phone_number = db.Column(db.String(12))
    key_abilities = db.Column(db.String(1000))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return f"""<User: {[
            getattr(self, col.name) 
            for col in User.__table__.columns 
            if col.name != 'password_hash'
        ]}>"""


class Organization(AuthMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), index=True, unique=True)
    email = db.Column(db.String(50), index=True)
    password_hash = db.Column(db.String(128))
    description = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    card = db.Column(db.Boolean)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))
    admins = db.relationship(
        'User', secondary=admins_org,
        primaryjoin=(admins_org.c.organization_id == id),
        secondaryjoin=(admins_org.c.user_id == User.id),
        backref=db.backref('organizations_admin', lazy='dynamic'),
        lazy='dynamic'
    )
    users = db.relationship(
        'User', secondary=volounteers,
        primaryjoin=(volounteers.c.organization_id == id),
        secondaryjoin=(volounteers.c.user_id == User.id),
        backref=db.backref('organizations', lazy='dynamic'),
        lazy='dynamic'
    )
    events = db.relationship(
        'Event',
        backref='organization',
        lazy='dynamic'
    )

    def __repr__(self):
        return f"""<User: {[
            getattr(self, col.name) 
            for col in Organization.__table__.columns 
            if col.name != 'password_hash'
        ]}>"""


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    description = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.String(20))
    chats = db.relationship('Chat', backref='event', lazy='dynamic')
    admins = db.relationship(
        'User', secondary=admins_event,
        primaryjoin=(admins_event.c.event_id == id),
        secondaryjoin=(admins_event.c.user_id == User.id),
        backref=db.backref('events_admin', lazy='dynamic'),
        lazy='dynamic'
    )
    users = db.relationship(
        'User', secondary=participants,
        primaryjoin=(participants.c.event_id == id),
        secondaryjoin=(participants.c.user_id == User.id),
        backref=db.backref('events', lazy='dynamic'),
        lazy='dynamic'
    )
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    weight = db.Column(db.Integer)

    def __repr__(self):
        return f"""<User: {[
            getattr(self, col.name) 
            for col in Event.__table__.columns 
        ]}>"""


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=uuid.uuid1().time)
    users = db.relationship('User', backref='card', lazy='dynamic')
    organizations = db.relationship('Organization', lazy='dynamic')


chat_user = db.Table(
    'chat-user',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'))
)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10000), nullable=False)
    attachment = db.Column(db.BLOB)
    pos_x = db.Column(db.Float)
    pos_y = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User') # FIXME
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='chat', lazy='dynamic', order_by=Message.created_at.desc())
    users = db.relationship(
        'User', secondary=chat_user,
        primaryjoin=(chat_user.c.chat_id == id),
        lazy='dynamic'
    )
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

@event.listens_for(Message, 'init')
def recieve_message_init(target, args, kwargs):
    author, chat = kwargs['author'], kwargs['chat']
    if author in chat.users:
        return kwargs
    else:
        raise ArgumentError("author must be in a chat")


@event.listens_for(Chat, 'init')
def recieve_chat_init(target, args, kwargs):
    chat_name = kwargs.get('name')
    if not chat_name:
        raise ArgumentError("Missing chat name")
    chat = Chat.query.filter_by(name=chat_name).first()
    if chat:
        raise ArgumentError("Chat name must be an unique")
    users = kwargs['users']
    for user in users:
        user = User.query.get(user.id)
        if not user:
            raise ArgumentError("User not found")
    return kwargs
