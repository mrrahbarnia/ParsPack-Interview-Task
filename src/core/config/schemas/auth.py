from pydantic_settings import BaseSettings


class Auth(BaseSettings):
    DEFAULT_USERNAME: str
    DEFAULT_PASSWORD: str
