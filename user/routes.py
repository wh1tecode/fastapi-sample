from fastapi import (
    APIRouter,
    status,
    Request,
    Depends,
)

from auth import (
    validate_access_token,
    custom_generate_unique_id,
    routing_authorization,
)
from tools import responses
from models import Model, MongoAggregation
from auth.contrib import Auth
from user.lib import CreateUser, UpdateUser
from fastapi.responses import JSONResponse

api = APIRouter(
    tags=["User"],
)
dynamic_model = Model()

@api.post(
    path="/user/create",
    openapi_extra={"operationId": "6682a9c24c688d0b3879f5b8"},
    generate_unique_id_function=custom_generate_unique_id,
)
@dynamic_model.create_user_model
async def user_create(
    request: Request,
):
    client_model = request.client_model
    username: str = client_model.username
    auth = await Auth.authenticate(request=request, username=username)
    if isinstance(auth, JSONResponse):
        return auth
    if auth:
        return responses.failed_response(
            data={},
            massage="duplicate username is not accepted",
            status=status.HTTP_302_FOUND,
        )
    user = CreateUser(request)
    response = await user.start_event_on_user()
    return response


@api.post(
    path="/user/update",
    openapi_extra={"operationId": "6682a830360760a4a878d424"},
    generate_unique_id_function=custom_generate_unique_id,
)
@routing_authorization
@dynamic_model.update_user_model
async def user_update(
    request: Request,
):
    client_model = request.client_model
    username: str = client_model.username
    if username:
        auth = await Auth.authenticate(username)
        if isinstance(auth, JSONResponse):
            return auth
        if auth:
            jsonresponse = responses.failed_response(
                data={},
                massage="username already exists",
                status=status.HTTP_400_BAD_REQUEST,
            )
            return jsonresponse
    user = UpdateUser(request=request)
    response = await user.start_event_on_user()
    return response


@api.get(
    path="/user/info",
    openapi_extra={"operationId": "6682a88e4c688d0b3879f5b6"},
    generate_unique_id_function=custom_generate_unique_id,
)
@routing_authorization
@dynamic_model.get_user_model
async def get_user(request: Request):
    orm = MongoAggregation(request)
    user = await orm.user_info()
    if not user:
        return responses.failed_response(
            data={}, massage="not any user", status=status.HTTP_404_NOT_FOUND
        )
    return responses.success_response(
        data=user,
        massage="user info",
        status=status.HTTP_200_OK,
    )