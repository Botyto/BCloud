from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID as PyUUID, uuid4

from ..data.sql.columns import Boolean, Bytes, DateTime, String, UUID, ForeignKey
from ..data.sql.columns import Mapped, mapped_column, relationship
from ..data.sql.database import Model

from .crypto import Passwords


class User(Model):
    __tablename__ = "User"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    username: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[bytes] = mapped_column(Bytes(2**32 - 1))
    logins: Mapped[List["Login"]] = relationship(back_populates="user")

    # project-specific fields
    display_name: Mapped[str] = mapped_column(String(256))

    def __init__(self, username: str, password: str):
        super().__init__()
        Passwords.validate(password)
        self.id = uuid4()
        self.created_at_utc = datetime.utcnow()
        self.enabled = True
        self.username = username
        self.password = Passwords.hash(password)
        # project-specific fields
        self.display_name = username

    def change_password(self, old_password: str, new_password: str):
        Passwords.validate(new_password)
        if not Passwords.compare(old_password, self.password):
            raise ValueError("Password mismatch")
        self.password = Passwords.hash(new_password)


class Login(Model):
    VALID_DURATION = timedelta(days=30)

    __tablename__ = "Login"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime)
    expire_at_utc: Mapped[datetime] = mapped_column(DateTime)
    last_used_utc: Mapped[datetime] = mapped_column(DateTime)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[PyUUID] = mapped_column(ForeignKey("User.id"), info={"owner": True})
    user: Mapped[User] = relationship(back_populates="logins", foreign_keys=[user_id])

    def __init__(self, user: User):
        self.id = uuid4()
        self.user_id = user.id
        self.user = user
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.created_at_utc = now
        self.expire_at_utc = now + self.VALID_DURATION
        self.last_used_utc = now
