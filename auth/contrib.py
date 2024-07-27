from models import database_beanie
from typing import Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from .utils import *
from tools import responses, utils, exceptions
from fastapi import status
from typing import Union
from memory import RedisSession
from jose import jwt
from tools import config
from bson.objectid import ObjectId
from datetime import datetime
from beanie.operators import Set
from redis.exceptions import ConnectionError


class Response:

    @staticmethod
    def save_error_response(self, response: JSONResponse):
        setattr(self.request, "response", response)
        setattr(self.request, "response_status", response.status_code)

    @staticmethod
    def save_response(self, response: JSONResponse):
        setattr(self.request, "response", response)
        setattr(self.request, "response_status", response.status_code)


class Auth:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @staticmethod
    async def authenticate(
        request: Request, username: str, password: str = None
    ) -> Union[database_beanie.User, JSONResponse, None]:
        redis = RedisSession()
        try:
            redis.check_redis_connection()
        except ConnectionError:
            return responses.failed_response(
                data={"redis": "redis connection error"},
                massage="internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        guest_token = request.cookies.get("guest_token")
        if not guest_token:
            jsonresponse = responses.failed_response(
                data={},
                massage=exceptions.guest_token_failed.detail,
                status=exceptions.guest_token_failed.status_code,
            )
            jsonresponse.headers.update(exceptions.guest_token_failed.headers)
            return jsonresponse
        user = await database_beanie.User.find_one(
            database_beanie.User.username == username,
        )
        if password:
            is_password_verified = verify_password(
                plain_hash=user.password, password=password
            )
            if is_password_verified:
                return user
        elif user:
            return user
        else:
            return None
        jsonresponse = responses.failed_response(
            data={},
            massage=exceptions.user_auth_failed.detail,
            status=exceptions.user_auth_failed.status_code,
        )
        jsonresponse.headers.update(exceptions.user_auth_failed.headers)
        return jsonresponse

    @staticmethod
    async def login(request: Request, user: database_beanie.User) -> JSONResponse:
        redis = RedisSession()
        try:
            redis.check_redis_connection()
        except ConnectionError:
            return responses.failed_response(
                data={"redis": "redis connection error"},
                massage="internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            await create_refresh_token(
                request=request,
                user=user,
            )
            await create_access_token(request=request)
            jsonresponse = responses.success_response(
                data={
                    "refresh_token": request.refresh_token,
                    "refresh_expire_date": request.refresh_expiration_time,
                    "fresh_token": request.fresh_token,
                    "fresh_expire_date": request.fresh_expiration_time,
                    "token_type": "bearer",
                },
                massage="user login",
                status=status.HTTP_200_OK,
            )
            jsonresponse.set_cookie(
                key="X-CSRF-ACCESS-TOKEN", value=request.fresh_token
            )
            return jsonresponse
        except Exception:
            jsonresponse = responses.failed_response(
                data={},
                massage=exceptions.login_failed.detail,
                status=exceptions.login_failed.status_code,
            )
            jsonresponse.headers.update(exceptions.login_failed.headers)
            return jsonresponse
        
    @staticmethod
    async def register(request: Request, user: database_beanie.User) -> JSONResponse:
        redis = RedisSession()
        try:
            redis.check_redis_connection()
        except ConnectionError:
            return responses.failed_response(
                data={"redis": "redis connection error"},
                massage="internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            await create_refresh_token(
                request=request,
                user=user,
            )
            await create_access_token(request=request)
            jsonresponse = responses.success_response(
                data={
                    "refresh_token": request.refresh_token,
                    "refresh_expire_date": request.refresh_expiration_time,
                    "fresh_token": request.fresh_token,
                    "fresh_expire_date": request.fresh_expiration_time,
                    "token_type": "bearer",
                },
                massage="user register",
                status=status.HTTP_200_OK,
            )
            jsonresponse.set_cookie(
                key="X-CSRF-ACCESS-TOKEN", value=request.fresh_token
            )
            return jsonresponse
        except Exception:
            jsonresponse = responses.failed_response(
                data={},
                massage=exceptions.login_failed.detail,
                status=exceptions.login_failed.status_code,
            )
            jsonresponse.headers.update(exceptions.login_failed.headers)
            return jsonresponse

    @staticmethod
    async def logout(request: Request):
        redis = RedisSession()
        try:
            redis.check_redis_connection()
        except ConnectionError:
            return responses.failed_response(
                data={"redis": "redis connection error"},
                massage="internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            access_token = request.cookies.get("X-CSRF-ACCESS-TOKEN", None)
            decoded_token = jwt.decode(
                token=access_token, key=config.SECRET_KEY, algorithms=config.ALGORITHM
            )
            decoded_token["fresh_token"] = access_token
            redis = RedisSession()
            if not redis.validate_session_access_token(decoded_token["sid"]):
                raise exceptions.access_token_failed
        except Exception:
            jsonresponse = responses.failed_response(
                data={},
                massage=exceptions.access_token_failed.detail,
                status=exceptions.access_token_failed.status_code,
            )
            jsonresponse.headers.update(exceptions.access_token_failed.headers)
            return jsonresponse
        redis = RedisSession()
        redis.delete_session_access_token(decoded_token["sid"])
        session = await database_beanie.Session.find_one(
            database_beanie.Session.id == ObjectId(decoded_token["sid"])
        )
        await session.update(
            Set({database_beanie.Session.expired_date: datetime.utcnow()})
        )
        data = utils.dumper(models=[session], exclude=["account_id"])
        return responses.success_response(
            data=data, massage="logout", status=status.HTTP_200_OK
        )

    @staticmethod
    async def create_fresh_token(request: Request, refresh_token: str) -> JSONResponse:
        redis = RedisSession()
        try:
            redis.check_redis_connection()
        except ConnectionError:
            return responses.failed_response(
                data={"redis": "redis connection error"},
                massage="internal server error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            decoded_token = await validate_refresh_token(refresh_token)
        except Exception:
            jsonresponse = responses.failed_response(
                data={},
                massage=exceptions.refresh_token_failed.detail,
                status=exceptions.refresh_token_failed.status_code,
            )
            jsonresponse.headers.update(exceptions.refresh_token_failed.headers)
            return jsonresponse
        await create_access_token(request=request, decoded_token=decoded_token)
        jsonresponse = responses.success_response(
            data={
                "fresh_token": request.fresh_token,
                "fresh_expire_date": request.fresh_expiration_time,
                "token_type": "bearer",
            },
            massage="fresh token",
            status=status.HTTP_201_CREATED,
        )
        jsonresponse.set_cookie(key="X-CSRF-ACCESS-TOKEN", value=request.fresh_token)
        return jsonresponse


class UploadCdnFile:

    def __init__(self):
        pass

    def delete(self, link: Optional[str] = None):
        try:
            utils.delete_file_cdn(link)
        except Exception:
            pass

    def upload_image(self, image: bytes, content_type: str) -> Optional[str]:
        """argument should be type of upload file"""
        try:
            if "image" in content_type:
                link = utils.upload_file_cdn(image)
                return link
        except Exception:
            pass
        return None

    def upload_video(self, video) -> Optional[str]: ...
