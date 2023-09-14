from sqlalchemy import String, select, update
from sqlalchemy.orm import Mapped, mapped_column

from ..data.sql.database import Session
from ..data.sql.database import Model


class Preference(Model):
    __tablename__ = "Preferences"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)


class PreferencesManager:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get(self, key: str, default: str = ""):
        statement = select(Preference) \
            .where(Preference.key == key)
        preference = self.session.scalars(statement).first()
        if preference is not None:
            return preference.value
        return default
    
    def set(self, key: str, value: str):
        statement = update(Preference) \
            .where(Preference.key == key) \
            .values(value=value)
        result = self.session.execute(statement)
        if result.rowcount == 0:
            preference = Preference(key=key, value=value)
            self.session.add(preference)
        self.session.commit()

    def get_dict(self):
        statement = select(Preference)
        preferences = self.session.scalars(statement).all()
        return {preference.key: preference.value for preference in preferences}
