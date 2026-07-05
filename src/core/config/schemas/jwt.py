from pydantic_settings import BaseSettings


class JWT(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRES_MINUTE: int
