from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

class Login(OAuth2PasswordRequestForm):

    def __init__(
        self,
        *,
        username: str,
        password: str,
        captcha_code: str = Form(default=None)
    ):
        super().__init__(
            username=username,
            password=password,
        )
        self.captcha_code = captcha_code


class Token(OAuth2PasswordBearer):

    def __init__(self, *, refresh_token: str = Form(...)):
        self.refresh_token = refresh_token
