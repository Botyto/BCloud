import bcrypt


class Passwords:
    MIN_LENGTH = 1
    MAX_LENGTH = 72  # bcrypt limitation
    SALT_LENGTH = 20
    
    def validate(self, password: str):
        if len(password) < self.MIN_LENGTH:
            raise ValueError("Password too short")
        if len(password) > self.MAX_LENGTH:
            raise ValueError("Password too long")

    def generate_salt(self):
        return bcrypt.gensalt().decode("ascii")

    def hash(self, password: str, salt: str|None = None):
        salt_bytes: bytes
        if salt is None:
            salt_bytes = bcrypt.gensalt()
        else:
            salt_bytes = salt.encode("ascii")
        hash_bytes = bcrypt.hashpw(password.encode("ascii"), salt_bytes)
        return hash_bytes.decode("ascii")

    def compare(self, password: str, hashed_password: str):
        return bcrypt.checkpw(password.encode("ascii"), hashed_password.encode("ascii"))
