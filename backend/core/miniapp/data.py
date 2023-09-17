from ..data.sql.columns import Mapped, mapped_column
from ..data.sql.columns import Boolean, Integer, String
from ..data.sql.database import Model


class MiniappEnable(Model):
    __tablename__ = "MiniappVersion"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean)


class MiniappVersion(Model):
    __tablename__ = "MiniappVersion"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    version: Mapped[int] = mapped_column(Integer)
