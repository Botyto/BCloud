from sqlalchemy import event
from sqlalchemy.orm import Session, QueryContext

from .handler import AuthError, AuthHandlerMixin

from ..data.sql.database import Model


class CheckingOwnershipContextManager:
    TAG = "checking_ownership"
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self):
        self.session.info[self.TAG] = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.info.pop(self.TAG)

def resolve_user_id(session: Session):
    if session.info.get(manual.DisableOwnershipChecksContextManager.TAG):
        return
    if session.info.get(CheckingOwnershipContextManager.TAG):
        return
    handler = session.info.get("handler")
    if handler is None:
        return
    if not isinstance(handler, AuthHandlerMixin):
        raise AuthError("Not authenticated")
    user_id = handler.get_current_user()
    if user_id is None:
        raise AuthError("Not authenticated")
    return user_id

@event.listens_for(Model, "load", propagate=True)
def on_instance_load(target: Model, context: QueryContext):
    session: Session = context.session
    user_id = resolve_user_id(session)
    if user_id is None:
        return
    with CheckingOwnershipContextManager(session):
        sharing.ensure_read_access(user_id, target)

@event.listens_for(Session, "before_flush")
def on_before_flush(session: Session, flush_context, instances):
    user_id = resolve_user_id(session)
    if user_id is None:
        return
    with CheckingOwnershipContextManager(session):
        for target in session.dirty:
            sharing.ensure_write_access(user_id, target)
