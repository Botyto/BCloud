import bcrypt


class Passwords:
    MIN_LENGTH = 1
    MAX_LENGTH = 72  # bcrypt limitation

    @classmethod
    def validate(cls, password: str):
        if len(password) < cls.MIN_LENGTH:
            raise ValueError("Password too short")
        if len(password) > cls.MAX_LENGTH:
            raise ValueError("Password too long")

    @classmethod
    def hash(cls, password: str, salt: bytes|None = None):
        if salt is None:
            salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("ascii"), salt)

    @classmethod
    def compare(cls, password: str, hashed_password: bytes):
        return bcrypt.checkpw(password.encode("ascii"), hashed_password)
