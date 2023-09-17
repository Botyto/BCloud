from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
from tornado.httputil import HTTPServerRequest
import user_agents
from uuid import UUID as PyUUID

from ..data.sql.columns import Boolean, Bytes, DateTime, String, UUID
from ..data.sql.columns import Mapped, mapped_column, relationship
from ..data.sql.database import Model

from .crypto import Passwords


class User(Model):
    __tablename__ = "User"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    username: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[bytes] = mapped_column(Bytes(2**32 - 1))

    def __init__(self, username: str, password: str):
        super().__init__()
        Passwords.validate(password)
        self.id = PyUUID()
        self.created_at_utc = datetime.utcnow()
        self.enabled = True
        self.username = username
        self.password = Passwords.hash(password)

    def change_password(self, old_password: str, new_password: str):
        Passwords.validate(new_password)
        if not Passwords.compare(old_password, self.password):
            raise ValueError("Password mismatch")
        self.password = Passwords.hash(new_password)


class DeviceKind(Enum):
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    MOBILE = "mobile"
    TABLET = "tablet"
    WEARABLE = "wearable"
    IOT = "iot"
    TV = "tv"
    BOT = "bot"
    UNKNOWN = "unknown"


class Device(Model):
    __tablename__ = "Device"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[PyUUID] = mapped_column(UUID)
    user: Mapped[User] = relationship(User, uselist=True, backref="devices")
    fingerprint: Mapped[str] = mapped_column(String(256))
    user_agent: Mapped[str] = mapped_column(String(256))

    def __init__(self, request: HTTPServerRequest):
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.created_at = now
        user_agent = request.headers.get("User-Agent", "Unknown")
        self.user_agent = user_agent
        self.fingerprint = self.get_fingerprint(request)
        agent = user_agents.parse(user_agent)
        if agent.is_pc:
            self.kind = DeviceKind.DESKTOP
        elif agent.is_tablet:
            self.kind = DeviceKind.TABLET
        elif agent.is_mobile:
            self.kind = DeviceKind.MOBILE
        elif agent.is_bot:
            self.kind = DeviceKind.BOT
        else:
            self.kind = DeviceKind.UNKNOWN

    @classmethod
    def get_fingerprint(cls, request: HTTPServerRequest) -> str:
        m = hashlib.sha256()
        m.update(request.headers.get("User-Agent", "Unknown").encode("utf-8"))
        return m.hexdigest()


class UserSession(Model):
    VALID_DURATION = timedelta(days=30)

    __tablename__ = "UserSession"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime)
    expire_at_utc: Mapped[datetime] = mapped_column(DateTime)
    last_used_utc: Mapped[datetime] = mapped_column(DateTime)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    user_id: Mapped[PyUUID] = mapped_column(UUID)
    user: Mapped[User] = relationship(User, uselist=True, backref="sessions")

    def __init__(self, user: User):
        self.id = PyUUID()
        self.user_id = user.id
        self.user = user
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        self.created_at_utc = now
        self.expire_at_utc = now + self.VALID_DURATION
