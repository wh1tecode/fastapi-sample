from fastapi import HTTPException, status


captcha_token_failed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Captcha Validation Error",
    headers={"WWW-Authenticate-Captcha": "Text"},
)

authenticate_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could Not Authenticate Token",
    headers={"WWW-Authenticate": "Bearer"},
)

authenticate_user = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Could Not Authenticate User",
    headers={"WWW-Authenticate": "Username & Password"},
)

guest_token_failed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Could Not Authenticate Guest Token",
    headers={"WWW-Authenticate-Guest-Token": "uuid"}
)

login_failed = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could Not Authenticate You",
    headers={"WWW-Authenticate-Login": "Bearer"},
)

access_token_failed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The provided access token is invalid or has expired. Please provide a valid access token and try again.",
    headers={"WWW-Authenticate-Fresh-Token": "Bearer"},
)

refresh_token_failed = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="The refresh token is invalid or has expired. Please re-authenticate to obtain a new refresh token.",
    headers={"WWW-Authenticate-Refresh-Token": "Bearer"},
)

user_permission_failed = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="You Are Not Enough Permissions",
    headers={"WWW-Authenticate-Permission": "Scopes"},
)

user_auth_failed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Auth Validation Error",
    headers={"WWW-Authenticate-Auth": "None"},
)

filter_failed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Filter Json Decoder",
    headers={"WWW-Authenticate-Auth": "Json"},
)

project_failed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Project Json Decoder",
    headers={"WWW-Authenticate-Auth": "Json"},
)

skip_failed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Skip Value Error",
    headers={"WWW-Authenticate-Auth": "Integer"},
)

limit_failed = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Limit Value Error",
    headers={"WWW-Authenticate-Auth": "Integer"},
)