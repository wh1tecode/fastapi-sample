from typing import Optional, Union
from datetime import datetime
from requests import request
import hashlib
import magic
from tools import config
from os.path import join
from functools import wraps
from traceback import print_exc
import inspect
from bson import ObjectId


def dumper(
    models: list,
    exclude: Optional[list] = None,
    exclude_none: bool = True,
    nested: bool = False,
) -> dict:
    """dumper for models

    Args:
        models (list): beanie model
        exclude (Optional[list], optional): parameters. Defaults to None.
        exclude_none (bool, optional): none parameters. Defaults to True.

    Returns:
        dict: return model dictionary
    """
    model = {}
    for mdl in models:
        try:
            model.update(mdl.model_dump(exclude=exclude, exclude_none=exclude_none))
        except Exception:
            model.update(mdl)
        for x in model:
            if isinstance(model[x], datetime):
                model.update({x: model[x].timestamp()})
    for x in exclude:
        delete_key_in_nested_dict(model, x)
    return model


def file_content_type(content: Union[bytes, None]) -> Union[bytes, None]:
    try:
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(content)
        if "image" in content_type or "video" in content_type:
            return content_type
    except Exception:
        pass


def upload_file_cdn(content: Union[bytes, None]) -> Union[str, None]:
    try:
        content_type = file_content_type(content)
        result = hashlib.md5(content)
        data = result.hexdigest()
        name = data + "." + content_type.split("/")[-1]
        url = join(config.NEXUS_URL, name)
        response = request(
            method="PUT",
            url=url,
            data=content,
            auth=(config.NEXUS_USERNAME, config.NEXUS_PASSWORD),
            timeout=1,
        )
        if response.status_code == 201:
            return url
    except Exception:
        pass
    return None


def delete_file_cdn(link: str) -> bool:
    response = request(
        method="DELETE",
        url=link,
        auth=(config.NEXUS_USERNAME, config.NEXUS_PASSWORD),
    )
    if response.status_code == 201:
        return True
    return False


def delete_key_in_nested_dict(d, key_to_delete):
    """
    Recursively delete a key from a nested dictionary.

    Parameters:
    - d (dict): The dictionary from which to delete the key.
    - key_to_delete (str): The key to delete from the dictionary.
    """
    if isinstance(d, dict):
        if key_to_delete in d:
            d.pop(key_to_delete)
        for key in d:
            delete_key_in_nested_dict(d[key], key_to_delete)
    elif isinstance(d, list):
        for item in d:
            delete_key_in_nested_dict(item, key_to_delete)


def save_errors(func):
    """save function class errors"""

    @wraps(func)
    async def wrap(*args, **kwargs):
        # before executing function
        returned_value = None
        try:
            if inspect.iscoroutinefunction(func):
                returned_value = await func(*args, **kwargs)
            else:
                returned_value = func(*args, **kwargs)
        except Exception as ex:
            print(print_exc())
            args[0].errors = ex
        # after execution function
        return returned_value

    return wrap


def clear_json_data(object_data: dict) -> dict:
    """clear dictionary from none value"""
    return {x: object_data[x] for x in object_data if object_data[x]}


def search_key_nested_dict(data, key):
    """
    Recursively search for a key in a nested dictionary or list.

    Parameters:
    - data: The dictionary or list to search.
    - key: The key to search for.

    Returns:
    - The value associated with the key if found, otherwise None.
    """
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for k, v in data.items():
            result = search_key_nested_dict(v, key)
            if result is not None:
                try:
                    return ObjectId(result)
                except Exception:
                    return None
    elif isinstance(data, list):
        for item in data:
            result = search_key_nested_dict(item, key)
            if result is not None:
                try:
                   return ObjectId(result)
                except Exception:
                    return None
    return None
