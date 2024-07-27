from fastapi import Query, UploadFile, File
from typing import Optional, Annotated, Union, Literal
from pydantic.json_schema import SkipJsonSchema
from models import schemas

class FirstName:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "first_name"
        self.min_length: int = 2
        self.max_length: int = 50
        self.pattern: str = r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$"
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(
            title=self.title,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[str]
        return (type_class, query)


class LastName:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "last_name"
        self.min_length: int = 2
        self.max_length: int = 50
        self.pattern: str = r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$"
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(
            title=self.title,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[str]
        return (type_class, query)


class PhoneNumber:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "phone_number"
        self.min_length: int = 11
        self.max_length: int = 12
        self.pattern: str = (
            r"^\+?[0-9]{1,3}?[-. ]?\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}$"
        )
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(
            title=self.title,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[str]
        return (type_class, query)


class EmailAddress:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "email_address"
        self.min_length: int = None
        self.max_length: int = None
        self.pattern: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(
            title=self.title,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[str]
        return (type_class, query)


class AvatarImage:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "avatar_image"
        self.required: bool = required

    def query(self) -> tuple:
        query = File(
            title=self.title,
        )
        type_class = UploadFile
        if not self.required:
            setattr(query, "default", None)
        return (type_class, query)


class BannerImage:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "banner_image"
        self.required: bool = required

    def query(self) -> tuple:
        query = File(
            title=self.title,
        )
        type_class = UploadFile
        if not self.required:
            setattr(query, "default", None)
        return (type_class, query)


class Gender:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "gender"
        self.min_digit: int = 0
        self.max_digit: int = 2
        self.pattern: str = None
        self.required = required

    def query(self) -> tuple:
        type_class = int
        query = Query(
            title=self.title,
            min_length=self.min_digit,
            max_length=self.max_digit,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[int]
        return (type_class, query)


class UserName:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "username"
        self.min_length: int = 4
        self.max_length: int = 30
        self.pattern: str = r"[a-zA-Z0-9_]"
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(
            title=self.title,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[str]
        return (type_class, query)


class PassWord:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "password"
        self.min_length: int = 4
        self.max_length: int = None
        self.pattern: str = None
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(
            title=self.title,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[str]
        return (type_class, query)


class IdField:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "id"
        self.min_length: int = 24
        self.max_length: int = 24
        self.pattern: str = "^[a-fA-F0-9]{24}$"
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(
            title=self.title,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[str]
        return (type_class, query)


class filter:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "filter"
        self.required = required

    def query(self) -> tuple:
        type_class = dict
        query = Query(title=self.title, description='{"filed1":"x", "filed2":2, ...}')
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[dict]
        return (type_class, query)


class project:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "project"
        self.required = required

    def query(self) -> tuple:
        type_class = dict
        query = Query(title=self.title, description='{"filed1":(1|0), ...}')
        if not self.required:
            setattr(query, "default", None)
            type_class = Optional[dict]
        return (type_class, query)


class sort:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "sort"
        self.min_length: int = 3
        self.max_length: int = 4
        self.pattern: str = "asc|desc"
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(
            title=self.title,
            min_length=self.min_length,
            max_length=self.max_length,
            pattern=self.pattern,
            description=self.pattern,
        )
        if not self.required:
            setattr(query, "default", "asc")
            type_class = Optional[str]
        return (type_class, query)


class skip:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "skip"
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(title=self.title, description="0> | ==0")
        if not self.required:
            setattr(query, "default", 0)
            type_class = Optional[str]
        return (type_class, query)


class limit:
    def __init__(self, required: bool = None) -> None:
        self.title: str = "limit"
        self.required = required

    def query(self) -> tuple:
        type_class = str
        query = Query(title=self.title, description="1> | ==1")
        if not self.required:
            setattr(query, "default", 1)
            type_class = Optional[str]
        return (type_class, query)
