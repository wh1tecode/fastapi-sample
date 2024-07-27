from fastapi import Depends, APIRouter, status, Response, Request, Security
from fastapi.responses import JSONResponse
from auth.models import Login
from fastapi.responses import StreamingResponse
from auth.utils import (
    refresh_token_csrf_header,
)
from uuid import uuid4
from tools import responses
from memory import RedisSession
from .contrib import Auth
from redis import ConnectionError
import io


router = APIRouter()


@router.get(path="/")
def guest(response: Response):
    redis = RedisSession()
    try:
        redis.check_redis_connection()
    except ConnectionError:
        return responses.failed_response(
            data={"redis": "redis connection error"},
            massage="internal server error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    guest_token = uuid4().hex + uuid4().hex
    response.set_cookie(key="guest_token", value=guest_token)
    return {"guest_token": guest_token}


@router.get(path="/simple_captcha")
async def simple_captcha(request: Request):
    guest_token = request.cookies.get("guest_token")
    redis = RedisSession()
    image = redis.simple_captcha(guest_token=guest_token, expire_seconds=360).get(
        b"image"
    )
    image_stream = io.BytesIO(image)
    return StreamingResponse(content=image_stream, media_type="image/jpeg")


@router.post(path="/login")
async def login(request: Request, form_data: Login = Depends()):
    user = await Auth.authenticate(
        request=request,
        username=form_data.username,
        password=form_data.password,
    )
    if isinstance(user, JSONResponse):
        return user
    login = await Auth.login(request=request, user=user)
    return login


@router.post(path="/token")
async def access_token(request: Request, refresh_token: str = Security(refresh_token_csrf_header)):
    access_token = await Auth.create_fresh_token(request=request, refresh_token=refresh_token)
    return access_token


@router.post(path="/logout")
async def logout(request: Request):
    logout = await Auth.logout(request)
    return logout
