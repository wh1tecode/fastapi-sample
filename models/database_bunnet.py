from bunnet import Document
from models import schemas
from datetime import datetime


class User(schemas.User, Document):

    created_date: datetime
    updated_date: datetime

    class Settings:
        name = "user"


class Session(schemas.Session, Document):

    expired_date: datetime
    created_date: datetime
    updated_date: datetime

    class Settings:
        name = "session"

class Route(schemas.Route, Document):

    created_date: datetime
    updated_date: datetime

    class Settings:
        name = "route"


class Group(schemas.Group, Document):

    created_date: datetime
    updated_date: datetime

    class Settings:
        name = "group"
