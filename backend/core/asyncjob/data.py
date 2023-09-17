from datetime import datetime, timedelta

from ..data.sql.columns import Mapped, mapped_column, Integer, String, JSON, DateTime, Interval
from ..data.sql.database import Model


class JobPromise(Model):
    __tablename__ = "JobPromise"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    issuer: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime)
    valid_for: Mapped[timedelta] = mapped_column(Interval)
    completed_at_utc: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    error: Mapped[str] = mapped_column(String(1024), default=None, nullable=True)
