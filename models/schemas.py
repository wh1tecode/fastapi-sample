from pydantic import BaseModel
from typing import Optional
from beanie import Link
from bson.objectid import ObjectId

class User(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    avatar_image: Optional[str] = None
    banner_image: Optional[str] = None
    gender: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_superuser: Optional[bool] = False
    scopes: Optional[list[str]] = ["all"]

class Session(BaseModel):
    user: Link[User]
    refresh_token: str
    cookies: Optional[dict] = None

    class Config:
        arbitrary_types_allowed = True

class Route(BaseModel):
    path: str

    class Config:
        arbitrary_types_allowed = True


class Group(BaseModel):
    route_id: ObjectId
    name: str

    class Config:
        arbitrary_types_allowed = True
