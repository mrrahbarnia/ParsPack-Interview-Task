from ....infra import BcryptPasswordEncryptor, AuthRepo, JWTService, JWT_INSTANCE


def get_jwt_service() -> JWTService:
    return JWT_INSTANCE


def get_password_encryptor() -> BcryptPasswordEncryptor:
    return BcryptPasswordEncryptor()


def get_repo() -> AuthRepo:
    return AuthRepo()
