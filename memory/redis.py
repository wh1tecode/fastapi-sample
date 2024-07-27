# from simpel_captcha import img_captcha
from tools import config
from redis import Redis
from fastapi import Request


class RedisSession():
    __instance = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RedisSession,cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, db=0):      
        if(self.__initialized): return
        self.__initialized = True
        self.redis = Redis(
            host=config.REDIS_HOST,
            port=int(config.REDIS_PORT),
            db=db,
            username=config.REDIS_USERNAME,
            password=config.REDIS_PASSWORD,
        )


    # def simple_captcha(self, guest_token: str, expire_seconds: int = 120) -> dict:
    #     img, code = img_captcha(byte_stream=True)
    #     self.redis.hset(
    #         f"user-session-captcha:{guest_token}",
    #         mapping={
    #             "image": img.getvalue(),
    #             "text": code,
    #         },
    #     )
    #     self.redis.expire(f"user-session-captcha:{guest_token}", time=expire_seconds)
    #     return self.redis.hgetall(f"user-session-captcha:{guest_token}")


    def validate_simple_captcha(self, guest_token: str, cap_text: str) -> bool:
        text = self.redis.hgetall(f"user-session-captcha:{guest_token}").get(b"text")
        if text:
            if text.lower().decode("utf-8") == cap_text:
                return True
            return False
        self.redis.delete(f"user-session-captcha:{guest_token}")
            

    def create_session_access_token(
            self,
            request: Request,
            expire_seconds: int, 
        ):
        self.redis.hset(
            f"user-session-access_token:{request.session_id}",
            mapping={
                "sid": request.session_id,
                "uid": request.user_id,
                "token": request.fresh_token,
            },
        )
        self.redis.expire(f"user-session-access_token:{request.session_id}", time=expire_seconds)
        return self.redis.hgetall(f"user-session-access_token:{request.session_id}")

    def validate_session_access_token(self, session_id: str):
        text = self.redis.hgetall(f"user-session-access_token:{session_id}")
        if text:
            return True
        return False
    
    def delete_session_access_token(self, session_id: str):
        self.redis.delete(f"user-session-captcha:{session_id}")
    
    def check_redis_connection(self):
        self.redis.ping()