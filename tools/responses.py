from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from typing import Union
from models import schemas
from fastapi import status


def success_response(
    data: Union[dict, list], massage: str, status: status = status.HTTP_201_CREATED,
) -> JSONResponse:
    """method for return success responses

    Parameters
    ----------
    inserted_doc_id : Document
        inserted document id

    Returns
    -------
    JSONResponse
    """

    content = schemas.Response(
        success=True,
        massage=f"{massage}",
        data=data,
    )
    response = JSONResponse(content=content.model_dump(), status_code=status)
    return response


def failed_response(
    data: Union[dict, list], massage: str, status: status = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """method for return success responses

    Parameters
    ----------
    inserted_doc_id : Document
        inserted document id

    Returns
    -------
    JSONResponse
    """

    content = schemas.Response(
        success=False,
        massage=f"{massage}",
        data=data,
    )
    return JSONResponse(content=content.model_dump(), status_code=status)

def failed_permission(
    data: Union[dict, list], massage: str, status: status = status.HTTP_401_UNAUTHORIZED
) -> JSONResponse:
    """method for return success responses

    Parameters
    ----------
    inserted_doc_id : Document
        inserted document id

    Returns
    -------
    JSONResponse
    """

    content = schemas.Response(
        success=False,
        massage=f"{massage}",
        data=data,
    )
    return HTTPException(status_code=status, detail=content.model_dump(), headers={"WWW-Authenticate": "Bearer scopes"})
