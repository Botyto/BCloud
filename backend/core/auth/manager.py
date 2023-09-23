from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from tornado.httputil import HTTPServerRequest
from uuid import UUID

from .crypto import Passwords
from .data import Login, User, UserRole
from .handlers import AuthError

from ..app.context import AppContext


class BaseManager:
    context: AppContext
    session: Session|None

    def __init__(self, context: AppContext, session: Session|None = None):
        self.context = context
        self.session = session

    def __enter__(self):
        if self.session is None:
            self.session = self.context.database.make_session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session is None:
            return
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()


class UserManager(BaseManager):
    @property
    def sensitive_authentication_errors(self):
        return self.context.env.debug

    def register(self, username: str, password: str, role: UserRole = UserRole.NEW):
        assert self.session is not None, "Session not initialized"
        statement = select(User).where(User.username == username)
        user = self.session.execute(statement).one_or_none()
        if user is not None:
            raise ValueError("Username taken")
        user = User(username, password, role)
        self.session.add(user)
        return user

    def login(self, username: str, password: str, http_request: HTTPServerRequest):
        assert self.session is not None, "Session not initialized"
        # user resolution
        statement = select(User).where(User.username == username)
        user = self.session.scalars(statement).one_or_none()
        if user is None:
            if self.sensitive_authentication_errors:
                raise AuthError("Invalid username")
            raise AuthError()
        # validation
        if not Passwords.compare(password, user.password):
            if self.sensitive_authentication_errors:
                raise AuthError("Invalid password")
            raise AuthError()
        # login creation
        login = Login(user)
        self.session.add(login)
        self.session.commit()
        data = {"sub": str(login.id)}
        return login, data

    def logout(self, login_id: UUID):
        assert self.session is not None, "Session not initialized"
        statement = select(Login).where(Login.id == login_id)
        login = self.session.scalars(statement).one_or_none()
        if login is None:
            if self.sensitive_authentication_errors:
                raise AuthError("Invalid login")
            raise AuthError()
        self.session.delete(login)

    def change_password(self, login_id: UUID, old_password: str, new_password: str, logout_all: bool = True):
        assert self.session is not None, "Session not initialized"
        statement = select(Login, User) \
            .where(Login.id == login_id) \
            .join(Login.user).add_columns(User)
        login: Login|None = self.session.scalars(statement).one_or_none()
        if login is None:
            if self.sensitive_authentication_errors:
                raise AuthError("Invalid login")
            raise AuthError()
        login.user.change_password(old_password, new_password)
        if logout_all:
            statement = delete(Login).where(Login.user_id == login.user_id)
            self.session.execute(statement)

    def delete_user(self, user_id: UUID):
        assert self.session is not None, "Session not initialized"
        statement = delete(User).where(User.id == user_id)
        self.session.execute(statement)

    def set_enabled(self, user_id: UUID, enabled: bool):
        assert self.session is not None, "Session not initialized"
        statement = select(User).where(User.id == user_id)
        user = self.session.scalars(statement).one_or_none()
        if user is None:
            raise ValueError("Invalid user")
        user.enabled = enabled
