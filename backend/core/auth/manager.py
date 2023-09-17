from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from uuid import UUID

from .crypto import Passwords
from .data import User, UserSession
from .handler import AuthError

from ..app.context import AppContext


class UserManager:
    context: AppContext
    session: Session|None

    def __init__(self, context: AppContext, session: Session|None = None):
        self.context = context
        self.session = session

    def __enter__(self):
        if self.session is None:
            self.context.database.make_session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session is None:
            return
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()

    @property
    def sensitive_authentication_errors(self):
        return self.context.env.debug

    def register(self, username: str, password: str):
        assert self.session is not None, "Session not initialized"
        statement = select(User).where(User.username == username)
        user = self.session.execute(statement).one_or_none()
        if user is not None:
            raise ValueError("Username taken")
        user = User(username, password)
        self.session.add(user)
        return user

    def login(self, username: str, password: str):
        assert self.session is not None, "Session not initialized"
        statement = select(User).where(User.username == username)
        user = self.session.scalars(statement).one_or_none()
        if user is None:
            if self.sensitive_authentication_errors:
                raise AuthError("Invalid username")
            raise AuthError()
        if not Passwords.compare(password, user.password):
            if self.sensitive_authentication_errors:
                raise AuthError("Invalid password")
            raise AuthError()
        session_obj = UserSession(user)
        self.session.add(session_obj)
        self.session.commit()
        data = {"sub": str(session_obj.id)}
        return user, data
    
    def logout(self, session_id: UUID):
        assert self.session is not None, "Session not initialized"
        statement = select(UserSession).where(UserSession.id == session_id)
        session_obj = self.session.scalars(statement).one_or_none()
        if session_obj is None:
            if self.sensitive_authentication_errors:
                raise AuthError("Invalid session")
            raise AuthError()
        self.session.delete(session_obj)

    def change_password(self, session_id: UUID, old_password: str, new_password: str, logout_all: bool = True):
        assert self.session is not None, "Session not initialized"
        statement = select(UserSession).where(UserSession.id == session_id)
        session_obj = self.session.scalars(statement).one_or_none()
        if session_obj is None:
            if self.sensitive_authentication_errors:
                raise AuthError("Invalid session")
            raise AuthError()
        session_obj.user.change_password(old_password, new_password)
        if logout_all:
            statement = delete(UserSession).where(UserSession.user_id == session_obj.user_id)
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
