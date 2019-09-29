from app import ma
from app import db

from app.models import User
from app.models import Organization
from app.models import Event
from app.models import Chat
from app.models import Message

from marshmallow import ValidationError
from marshmallow import post_load
from marshmallow import validates_schema
from marshmallow.fields import Nested, Str, Integer, DateTime, Pluck


class BaseSchema(ma.ModelSchema):
    class Meta:
        sqla_session = db.session


class UserSchema(ma.ModelSchema):
    class Meta(BaseSchema.Meta):
        model = User

    password_hash = Str(load_only=True)
    email = Str(load_only=True)
    organizations = Nested("OrganizationSchema", many=True, exclude=("users", ))
    organizations_admin = Nested("OrganizationSchema", many=True, exclude=("admins", ))
    events = Nested("EventSchema", many=True, exclude=("users", ))
    events_admin = Nested("EventSchema", many=True, exclude=("admins", ))

    _links = ma.Hyperlinks({
        'self': ma.URLFor('main.get_profile', pk='<id >'),
        'edit': ma.URLFor('main.edit_user', pk='<id >')
    })


class OrganizationSchema(ma.ModelSchema):
    class Meta(BaseSchema.Meta):
        model = Organization
        load_only = ('password_hash', 'email', )

    password_hash = Str(load_only=True)
    email = Str(load_only=True)
    users = Nested("UserSchema", many=True, exclude=("organizations", ))
    admins = Nested("UserSchema", many=True, exclude=("organizations", ))
    events = Nested("EventSchema", many=True, exclude=("organization", ))

    _links = ma.Hyperlinks({
        'self': ma.URLFor('main.get_organization', pk='<id >'),
        'edit': ma.URLFor('main.edit_organization', pk='<id>'),
        'collection': ma.URLFor('main.get_organizations'),
        # 'admins': ma.List(ma.HyperlinkRelated('main.get_organization_admins')),
        # 'users': ma.List(ma.HyperlinkRelated('main.get_organization_users'))
    })


class EventSchema(ma.ModelSchema):
    class Meta(BaseSchema.Meta):
        model = Event

    users = Nested("UserSchema", many=True, exclude=("events", ))
    admins = Nested("UserSchema", many=True, exclude=("events_admin", ))
    organization = Nested("OrganizationSchema", many=False, exclude=("events", ))

    _links = ma.Hyperlinks({
        'self': ma.URLFor('main.get_event', pk='<id >'),
        'edit': ma.URLFor('main.edit_event', pk='<id >'),
        'collection': ma.URLFor('main.get_events'),
        # 'admins': ma.List(ma.HyperlinkRelated('main.get_event_users')),
        # 'users': ma.List(ma.HyperlinkRelated('main.get_event_admins'))
    })


class ChatSchema(ma.ModelSchema):
    id = Integer(required=False, data_key="chat")
    name = Str(required=True)
    created_at = DateTime(required=False)
    messages = Nested('MessageSchema', many=True, exclude=('chat', ), required=False)
    users = Pluck('UserSchema', 'id', many=True, required=True)
    event = Pluck('EventSchema', 'id', many=False, required=True)

    class Meta(BaseSchema.Meta):
        model = Chat


class MessageSchema(ma.ModelSchema):
    id = Integer(required=False)
    text = Str(required=True)
    created_at = DateTime(required=False)
    author = Pluck('UserSchema', "id", required=True, many=False)
    chat = Pluck('ChatSchema', "id", required=True, many=False)

    class Meta(BaseSchema.Meta):
        model = Message
        
