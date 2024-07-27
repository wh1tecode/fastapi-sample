from .schemas import User
from functools import wraps
from fastapi import Request
from models.feild import *
from fastapi import Depends
from fastapi.params import File
import inspect
from auth.contrib import UploadCdnFile
from json import loads, JSONDecodeError
from tools import responses, exceptions
from fastapi_pagination import Params
from pydantic import BaseModel, create_model


class Model:

    def __init__(self, **kwargs):
        self.required = kwargs.get("required")
        self.is_filterable = kwargs.get("is_filterable")
        self.is_projection_able = kwargs.get("is_projection_able")

    def user(self, *args) -> BaseModel:
        user = User()
        field_definitions = {}
        base_fields = {}
        user_base_fields = {
            field: (user.__annotations__[field], ...) for field in user.__annotations__
        }
        base_fields.update(user_base_fields)
        base_fields.pop("owner_id", None)
        for arg in args:
            query = arg.query()
            if self.required:
                if arg.required is None:
                    arg.required = True
                    query = arg.query()
            field_definitions.update({arg.title: query})
        query_params = {**base_fields}
        query_params.update(field_definitions)
        return create_model("User", **field_definitions)

    async def generate_request_items(self, request, client_model, kwargs):
        from starlette.datastructures import UploadFile

        setattr(request, "paginator", kwargs.pop("paginator", None))
        model_fields = {item for item in client_model.model_fields}
        json_data = {}
        for field in model_fields:
            if isinstance(kwargs[field], UploadFile):
                upload_file = UploadCdnFile()
                kwargs[field] = upload_file.upload_image(
                    image=await kwargs[field].read(),
                    content_type=kwargs[field].content_type,
                )
            json_data[field] = kwargs[field]
            setattr(client_model, field, kwargs[field])
        for item in model_fields:
            kwargs.pop(item)
        setattr(client_model, "json_data", json_data)
        setattr(request, "client_model", client_model)

    def cleaned_update_model(self, request, kwargs):
        is_superuser: bool = getattr(request, "is_superuser", None)
        if not is_superuser:
            kwargs["id"] = None

    def cleaned_get_model(self, request, kwargs):
        is_superuser: bool = getattr(request, "is_superuser", None)
        try:
            if kwargs["skip"]:
                kwargs["skip"] = int(kwargs["skip"])
                if kwargs["skip"] < 0:
                    kwargs["skip"] = 0
            else:
                kwargs["skip"] = {}
        except ValueError:
            return responses.failed_response(
                data={},
                massage=exceptions.skip_failed.detail,
                status=exceptions.skip_failed.status_code,
            )
        try:
            if kwargs["limit"]:
                kwargs["limit"] = int(kwargs["limit"])
                if kwargs["limit"] < 1:
                    kwargs["limit"] = 1
            else:
                kwargs["limit"] = {}
        except ValueError:
            return responses.failed_response(
                data={},
                massage=exceptions.limit_failed.detail,
                status=exceptions.limit_failed.status_code,
            )
        if not is_superuser:
            kwargs["filter"] = {}
            kwargs["project"] = {}
            return
        try:
            if kwargs["filter"]:
                kwargs["filter"] = loads(kwargs["filter"])
            else:
                kwargs["filter"] = {}
        except JSONDecodeError:
            return responses.failed_response(
                data={},
                massage=exceptions.filter_failed.detail,
                status=exceptions.filter_failed.status_code,
            )
        try:
            if kwargs["project"]:
                kwargs["project"] = loads(kwargs["project"])
            else:
                kwargs["project"] = {}
        except JSONDecodeError:
            return responses.failed_response(
                data={},
                massage=exceptions.project_failed.detail,
                status=exceptions.project_failed.status_code,
            )

    def create_user_model(self, func):
        sig = inspect.signature(func)
        new_params = list(sig.parameters.values())
        self.required = True
        client_model = self.user(
            FirstName(),
            LastName(),
            PhoneNumber(required=False),
            EmailAddress(required=False),
            UserName(),
            PassWord(),
            Gender(),
            AvatarImage(required=False),
            BannerImage(required=False),
        )
        for name, default in client_model.model_fields.items():
            if isinstance(default, File):
                new_params.append(
                    inspect.Parameter(
                        name,
                        inspect.Parameter.KEYWORD_ONLY,
                        annotation=Annotated[UploadFile, File()],
                        default=default.default,
                    )
                )
            else:
                new_params.append(
                    inspect.Parameter(
                        name, inspect.Parameter.KEYWORD_ONLY, default=default
                    )
                )
        new_sig = sig.replace(parameters=new_params)

        @wraps(func)
        async def wrap(*args, **kwargs):
            request: Request = kwargs.get("request", None)
            if request:
                await self.generate_request_items(request, client_model, kwargs)
            if inspect.iscoroutinefunction(func):
                returned_value = await func(*args, **kwargs)
            else:
                returned_value = func(*args, **kwargs)
            return returned_value

        wrap.__signature__ = new_sig
        return wrap

    def update_user_model(self, func):
        sig = inspect.signature(func)
        new_params = list(sig.parameters.values())
        self.required = False
        client_model = self.user(
            IdField(),
            FirstName(),
            LastName(),
            PhoneNumber(),
            EmailAddress(),
            UserName(),
            PassWord(),
            Gender(),
            AvatarImage(),
            BannerImage(),
        )
        for name, default in client_model.model_fields.items():
            if isinstance(default, File):
                new_params.append(
                    inspect.Parameter(
                        name,
                        inspect.Parameter.KEYWORD_ONLY,
                        annotation=Annotated[UploadFile, File()],
                        default=default.default,
                    )
                )
            else:
                new_params.append(
                    inspect.Parameter(
                        name, inspect.Parameter.KEYWORD_ONLY, default=default
                    )
                )

        new_sig = sig.replace(parameters=new_params)

        @wraps(func)
        async def wrap(*args, **kwargs):
            request: Request = kwargs.get("request", None)
            if request:
                self.cleaned_update_model(request, kwargs)
                await self.generate_request_items(request, client_model, kwargs)
            if inspect.iscoroutinefunction(func):
                returned_value = await func(*args, **kwargs)
            else:
                returned_value = func(*args, **kwargs)

            return returned_value

        wrap.__signature__ = new_sig
        return wrap

    def get_user_model(self, func):
        sig = inspect.signature(func)
        new_params = list(sig.parameters.values())
        self.required = False
        client_model = self.user(filter(), project(), sort(), skip(), limit())
        for name, default in client_model.model_fields.items():
            new_params.append(
                inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY, default=default)
            )
        new_params.append(
            inspect.Parameter(
                "paginator", inspect.Parameter.KEYWORD_ONLY, default=Depends(Params)
            )
        )
        new_sig = sig.replace(parameters=new_params)

        @wraps(func)
        async def wrap(*args, **kwargs):
            request: Request = kwargs.get("request", None)
            if request:
                if failed := self.cleaned_get_model(request, kwargs):
                    return failed
                await self.generate_request_items(request, client_model, kwargs)
            if inspect.iscoroutinefunction(func):
                returned_value = await func(*args, **kwargs)
            else:
                returned_value = func(*args, **kwargs)

            return returned_value

        wrap.__signature__ = new_sig
        return wrap
