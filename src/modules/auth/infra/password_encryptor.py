from passlib.context import CryptContext


class BcryptPasswordEncryptor:
    def __init__(self) -> None:
        self._context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def encrypt(self, password: str) -> str:
        return self._context.hash(password)

    def verify(self, password: str, encrypted: str) -> bool:
        return self._context.verify(password, encrypted)
