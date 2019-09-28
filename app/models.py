from app import db

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