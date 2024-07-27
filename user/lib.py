from models import database_beanie
from fastapi import Request, status
from fastapi.responses import JSONResponse
from auth import (
    hash_password,
)
from auth.contrib import Auth
from auth.contrib import UploadCdnFile
from tools import utils
from abc import ABC, abstractmethod
from datetime import datetime
from redis import ConnectionError as redis_connection_error
from typing import Optional
from tools import responses


class User(ABC):
    def __init__(self, request: Request):
        self.request: Request = request
        self.client_model = request.client_model
        self.username: str = self.client_model.username
        self.password: str = self.client_model.password
        self.first_name: str = self.client_model.first_name
        self.last_name: str = self.client_model.last_name
        self.phone_number: str = self.client_model.phone_number
        self.email_address: str = self.client_model.email_address
        self.gender: str = self.client_model.gender
        self.avatar_link: str = self.client_model.avatar_image
        self.banner_link: str = self.client_model.banner_image
        self.user_id: str = getattr(request, "user_id", None)
        self.is_superuser: str = getattr(request, "is_superuser", None)
        self.json_data: dict = self.client_model.json_data
        self.created_date = datetime.utcnow()
        self.updated_date = datetime.utcnow()

    @abstractmethod
    def start_event_on_user(self):
        pass

    @abstractmethod
    def get_json_data(self):
        pass

    @abstractmethod
    def get_json_error(self):
        pass


class CreateUser(User):
    errors = None

    def __init__(self, request: Request):
        super().__init__(request)

    @utils.save_errors
    async def user_create_user(self) -> Optional[JSONResponse]:
        self.user = database_beanie.User(
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number=self.phone_number,
            email_address=self.email_address,
            avatar_image=self.avatar_link,
            banner_image=self.banner_link,
            gender=self.gender,
            username=self.username,
            password=hash_password(self.password),
            created_date=self.created_date,
            updated_date=self.updated_date,
        )
        await self.user.create()
        register = await Auth.register(request=self.request, user=self.user)
        return register

    async def start_event_on_user(self) -> JSONResponse:
        register = await self.user_create_user()
        if self.errors:
            session = await database_beanie.Session.find_one(
                database_beanie.Session.user == self.user
            )
            await session.delete()
            await self.user.delete()
            jsonresponse = responses.success_response(
                data=self.get_json_error(),
                massage="internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return jsonresponse
        return register

    def get_json_data(self):
        self.json_data["created_date"] = int(self.user.created_date.timestamp())
        return utils.clear_json_data(self.json_data)

    def get_json_error(self):
        if isinstance(self.errors, redis_connection_error):
            return {"redis": "redis connection error"}
        return {"internal": "server error"}


class UpdateUser(User):
    errors = None

    def __init__(self, request: Request):
        super().__init__(request)

    @utils.save_errors
    async def user_update_user(self):
        self.user: database_beanie.User = await database_beanie.User.get(self.user_id)
        if not self.user:
            return None
        upload_file = UploadCdnFile()
        if self.user.avatar_image:
            upload_file.delete(link=self.user.avatar_image)
        if self.user.banner_image:
            upload_file.delete(link=self.user.banner_image)
        if self.first_name:
            self.user.first_name = self.first_name
        if self.last_name:
            self.user.last_name = self.last_name
        if self.phone_number:
            self.user.phone_number = self.phone_number
        if self.email_address:
            self.user.email_address = self.email_address
        if self.gender:
            self.user.gender = self.gender
        if self.username:
            self.user.username = self.username
        if self.password:
            self.user.password = hash_password(self.password)
        self.user.avatar_image = self.avatar_link
        self.user.banner_image = self.banner_link
        self.user.updated_date = datetime.utcnow()
        await self.user.save()
        return self.user

    @utils.save_errors
    async def admin_update_user(self):
        self.user: database_beanie.User = await database_beanie.User.get(
            self.client_model.id
        )
        if not self.user:
            return None
        upload_file = UploadCdnFile()
        if self.user.avatar_image:
            upload_file.delete(link=self.user.avatar_image)
        if self.user.banner_image:
            upload_file.delete(link=self.user.banner_image)
        if self.first_name:
            self.user.first_name = self.first_name
        if self.last_name:
            self.user.last_name = self.last_name
        if self.phone_number:
            self.user.phone_number = self.phone_number
        if self.email_address:
            self.user.email_address = self.email_address
        if self.gender:
            self.user.gender = self.gender
        if self.username:
            self.user.username = self.username
        if self.password:
            self.user.password = hash_password(self.password)
        self.user.avatar_image = self.avatar_link
        self.user.banner_image = self.banner_link
        self.user.updated_date = datetime.utcnow()
        await self.user.save()
        return self.user

    async def start_event_on_user(self) -> JSONResponse:
        if self.errors:
            jsonresponse = responses.success_response(
                data=self.get_json_error(),
                massage="internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return jsonresponse
        if self.is_superuser and self.client_model.id:
            user = await self.admin_update_user()
        else:
            user = await self.user_update_user()
        if not user:
            jsonresponse = responses.success_response(
                data={},
                massage="not any user",
                status=status.HTTP_404_NOT_FOUND,
            )
            return jsonresponse
        jsonresponse = responses.success_response(
            data=self.get_json_data(),
            massage="user update",
            status=status.HTTP_200_OK,
        )
        return jsonresponse

    def get_json_data(self):
        self.json_data["updated_date"] = int(self.user.updated_date.timestamp())
        return utils.clear_json_data(self.json_data)

    def get_json_error(self):
        return {"internal": "server error"}
