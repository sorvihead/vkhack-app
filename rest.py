from app import create_app, db
from app.models import User, Organization, Event
from app.schemas import UserSchema, OrganizationSchema, EventSchema

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Organization': Organization, 'Event': Event, 'UserSchema': UserSchema,
     'OrganizationSchema': OrganizationSchema, 'EventSchema': EventSchema}