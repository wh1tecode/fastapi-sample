from jose import jwt
from datetime import timedelta, datetime
from typing import Optional
from fastapi import Depends, Request, status, Query
from fastapi.exceptions import HTTPException
from typing import Union
from tools import exceptions
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from models import database_beanie
from tools import config
from fastapi.security import SecurityScopes, APIKeyHeader
from tools import responses
from bson.objectid import ObjectId
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from functools import wraps
from memory import RedisSession
from fastapi.routing import APIRoute
import inspect
from tools import utils
from beanie.operators import Set


PH = PasswordHasher()

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/token",
# )

refresh_token_csrf_header = APIKeyHeader(
    name="X-CSRF-REFRESH-TOKEN",
    scheme_name="X-CSRF-REFRESH-TOKEN",
    description="Fill in the csrf refresh "
    "token when authorization is "
    "required, and use the csrf "
    "refresh token when the token "
    "needs to be refreshed",
)


async def create_refresh_token(
    request: Request,
    user: database_beanie.User,
    expiration_days: Optional[int] = 365,
) -> tuple:
    user_id = str(user.id)
    expiration_time = datetime.utcnow() + timedelta(days=expiration_days)
    session = database_beanie.Session(
        user=user,
        refresh_token="#Defaults:"+user_id,
        expired_date=expiration_time,
        created_date=datetime.utcnow(),
        updated_date=datetime.utcnow(),
    )
    await session.create()
    session_id = str(session.id)
    token = jwt.encode(
        claims={
            "uid": user_id,
            "sid": session_id,
            "is_superuser": user.is_superuser,
            "scopes": user.scopes,
            "exp": expiration_time,
        },
        key=config.SECRET_REFRESH,
        algorithm=config.ALGORITHM,
    )
    await session.update(Set({database_beanie.Session.refresh_token: token}))
    
    setattr(request, "user_id", user_id)
    setattr(request, "session_id", session_id)
    setattr(request, "refresh_expiration_time", expiration_time.timestamp())
    setattr(request, "is_superuser", user.is_superuser)
    setattr(request, "refresh_token", token)
    setattr(request, "scopes", user.scopes)


async def create_access_token(
    request: Request,
    decoded_token: Optional[dict] = None,
    expiration_seconds: Optional[int] = 3600,
) -> tuple:
    expiration_time = datetime.utcnow() + timedelta(seconds=expiration_seconds)
    token = jwt.encode(
        claims={
            "uid": decoded_token.get("uid") if decoded_token else request.user_id,
            "sid": decoded_token.get("sid") if decoded_token else request.session_id,
            "is_superuser": decoded_token.get("is_superuser") if decoded_token else request.is_superuser,
            "scopes": decoded_token.get("scopes") if decoded_token else request.scopes,
            "exp": expiration_time,
        },
        key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )
    setattr(request, "fresh_token", token)
    setattr(request, "fresh_expiration_time", expiration_time.timestamp())
    redis = RedisSession()
    redis.create_session_access_token(
        request=request,
        expire_seconds=expiration_seconds,
    )


async def validate_refresh_token(
    token: str,
) -> Union[dict, HTTPException]:
    try:
        decoded_token = jwt.decode(
            token=token, key=config.SECRET_REFRESH, algorithms=config.ALGORITHM
        )
        decoded_token["refresh_token"] = token
        session = await database_beanie.Session.find_one(
            database_beanie.Session.id == ObjectId(decoded_token["sid"])
        )
        if not session:
            raise exceptions.refresh_token_failed
        elif session.expired_date < datetime.utcnow():
            raise exceptions.refresh_token_failed
        return decoded_token
    except Exception:
        raise exceptions.refresh_token_failed


def validate_access_token(
    request: Request,
) -> Union[dict, HTTPException]:
    try:
        access_token = request.cookies.get("X-CSRF-ACCESS-TOKEN", None)
        decoded_token = jwt.decode(
            token=access_token, key=config.SECRET_KEY, algorithms=config.ALGORITHM
        )
        decoded_token["fresh_token"] = access_token
        redis = RedisSession()
        if not redis.validate_session_access_token(decoded_token["sid"]):
            raise exceptions.access_token_failed
        return decoded_token
    except Exception:
        raise exceptions.access_token_failed


def hash_password(password: str) -> str:
    try:
        hashed_password = PH.hash(password)
        return hashed_password
    except Exception as ex:
        return None


def verify_password(plain_hash: str, password: str) -> bool:
    try:
        if PH.verify(hash=plain_hash, password=password):
            return True
    except VerifyMismatchError:
        return False


async def permission_by(
    security_scopes: SecurityScopes, token: dict = Depends(validate_access_token)
) -> Union[dict, None]:
    """This function provided for permission on routes.

    Args:
        security_scopes (SecurityScopes): rec
        token (dict, optional): _description_. Defaults to Depends(validate_access_token).

    Returns:
        bool: _description_
    """

    route_scopes = security_scopes.scopes

    payload_scopes = token.get("scopes", [])

    for scope in payload_scopes:
        if scope in route_scopes:
            return token

    raise responses.failed_permission(data={}, massage="permission denied")


def _pad(s):
    return s + (AES.block_size - len(s) % AES.block_size) * chr(
        AES.block_size - len(s) % AES.block_size
    )


def _unpad(s):
    return s[: -ord(s[len(s) - 1 :])]


def aes_encrypt(raw: str):
    key = hashlib.sha256(config.AES_KEY.encode()).digest()
    raw = _pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw.encode())).decode()


def aes_decrypt(enc: str):
    key = hashlib.sha256(config.AES_KEY.encode()).digest()
    enc = base64.b64decode(enc)
    iv = enc[: AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return _unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")


def routing_authorization(func):
    """Permission on route
       Use request object fastapi
       into route to get token info

    Args:
        func (_type_): _description_

    Returns:
        _type_: _description_
    """

    @wraps(func)
    async def wrap(*args, **kwargs):
        # before executing function
        request: Request = kwargs.get("request", None)
        if request:
            # validate fresh token
            try:
                operation_id = request.app.openapi()["paths"][request.url.path][
                    request.method.lower()
                ]["operationId"]
                fr_token = validate_access_token(request)
                setattr(request, "user_id", fr_token["uid"])
                setattr(request, "session_id", fr_token["sid"])
                setattr(request, "is_superuser", fr_token["is_superuser"])
                setattr(request, "scopes", fr_token["scopes"])
                permission_list_on_route = [
                    x["name"]
                    for x in await database_beanie.Group.aggregate(
                        [
                            {"$match": {"route_id": ObjectId(operation_id)}},
                            {"$project": {"_id": 0, "name": 1}},
                        ]
                    ).to_list()
                ]
                if request.scopes[0] not in permission_list_on_route:
                    return responses.failed_response(
                        data={},
                        massage=exceptions.user_permission_failed.detail,
                        status=exceptions.user_permission_failed.status_code,
                    )
            except Exception as ex:
                return responses.failed_response(
                    data={},
                    massage=ex.detail,
                    status=ex.status_code,
                )
        if inspect.iscoroutinefunction(func):
            returned_value = await func(*args, **kwargs)
        else:
            returned_value = func(*args, **kwargs)

        # after execution function

        return returned_value

    return wrap


def generate_dynamic_fields():
    """
    Dynamically generate FastAPI query parameters based on some logic.
    For demonstration purposes, a static set of fields is returned.
    """
    dynamic_fields = {
        "field1": Query(None, title="Field 1"),
        "field2": Query(None, title="Field 2"),
        # Add more fields as needed
    }
    return dynamic_fields


def captcha_authorization(func):
    """Provide for append captcha to route
        append field captcha_code to route
        that needs to captcha authorization
    Args:
        func: route

    Returns:
        def: func
    """

    @wraps(func)
    async def wrap(*args, **kwargs):
        # before executing function
        request: Request = kwargs.get("request", None)
        captcha_code: str = kwargs.get("captcha_code")
        gust_token = request.cookies.get("guest_token", None)
        if not gust_token:
            return responses.failed_response(
                data={},
                massage="guest_token required be in cookies",
                status=status.HTTP_400_BAD_REQUEST,
            )
        redis = RedisSession()
        if not redis.validate_simple_captcha(gust_token, captcha_code):
            return responses.failed_response(
                data={},
                massage="captcha is not match",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            returned_value = await func(*args, **kwargs)
        except Exception as ex:
            returned_value = func(*args, **kwargs)

        # after execution function

        return returned_value

    return wrap


def custom_generate_unique_id(route: APIRoute):
    return route.openapi_extra.get("operationId", None) if route.openapi_extra else None


async def set_default_group(app):
    paths = app.openapi()["paths"]
    utc_date = datetime.utcnow()
    for path in paths:
        operation_id = utils.search_key_nested_dict(data=paths[path], key="operationId")
        if operation_id:
            route = database_beanie.Route(path=path, created_date=utc_date)
            if not await database_beanie.Group.find_one(
                database_beanie.Group.route_id == operation_id,
                database_beanie.Group.name == "all",
            ):
                group = database_beanie.Group(
                    route_id=operation_id,
                    name="all",
                    created_date=utc_date,
                    updated_date=utc_date,
                )
                await group.save()
                await route.save()
