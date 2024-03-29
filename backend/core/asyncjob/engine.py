from datetime import datetime, timedelta
import logging
from sqlalchemy import not_, select
from sqlalchemy.orm import object_session
from threading import current_thread, Thread
from typing import Any, Dict, Type

from .action import Action
from .context import AsyncJobContext, AsyncJobRuntimeContext
from .data import JobPromise
from .handlers import JobHandlers, AsyncJobHandler
from .state import State

from ..cronjob.schedule import Schedule
from ..data.sql.columns import ensure_str_fit, utcnow_tz

logger = logging.getLogger(__name__)


class AsyncJobs:
    context: AsyncJobContext
    states: Dict[int, State]
    threads: Dict[int, Thread]
    handlers: JobHandlers

    def __init__(self, context: AsyncJobContext):
        self.context = context
        self.states = {}
        self.threads = {}
        self.handlers = JobHandlers()

    def start(self):
        self.context.cron.schedule(self.__resume_jobs, Schedule.hourly())
        self.context.cron.schedule(self.__delete_expired_jobs, Schedule.daily())
        self.__resume_jobs()

    # TODO limit number of jobs running at once
    def schedule(self, issuer: str, type: str, payload: dict|Any|None, valid_for: timedelta|None = None) -> int:
        assert ensure_str_fit("issuer", issuer, JobPromise.issuer, should_raise=False)
        ensure_str_fit("type", type, JobPromise.type)
        if payload is None:
            payload = {}
        elif not isinstance(payload, dict):
            payload = {k: getattr(payload, k) for k in payload.__annotations__}
            handler = self.__resolve_handler_type(issuer, type)
            if handler is not None:
                handler.verify_payload(payload)
        if valid_for is None:
            valid_for = timedelta()
        with self.context.database.make_session() as session:
            promise = JobPromise()
            promise.issuer = issuer
            promise.type = type
            promise.payload = payload
            promise.valid_for = valid_for
            promise.created_at_utc = utcnow_tz()
            session.add(promise)
            session.commit()
            self.__start_job(promise)
            return promise.id

    def delete(self, job: JobPromise):
        state = self.states.get(job.id)
        if state is not None:
            state.cancel()
        handler_type = self.__resolve_handler_type(job.issuer, job.type)
        if handler_type is not None:
            try:
                logger.debug("Deleting job #%d", job.id)
                context = AsyncJobRuntimeContext(self.context, self.states.get(job.id), job.id, job.payload)
                handler = handler_type(context)
                handler.delete()
            except Exception as e:
                logger.error("Job #%d failed to delete", job.id)
                logger.exception(e)
        session = object_session(job)
        assert session is not None
        session.delete(job)

    def cancel(self, job: JobPromise):
        self.delete(job)

    def __resolve_handler_type(self, issuer: str, type: str) -> Type[AsyncJobHandler]|None:
        return self.handlers.resolve(issuer, type)

    def __job_proc(self, handler_type: Type[AsyncJobHandler], action: Action, job_id: int, payload: dict):
        state = State()
        self.states[job_id] = state
        self.threads[job_id] = current_thread()
        try:
            logger.debug("Starting job #%d", job_id)
            context = AsyncJobRuntimeContext(self.context, state, job_id, payload)
            handler = handler_type(context)
            handler.trigger(action)
        except Exception as e:
            logger.error("Job #%d failed", job_id)
            error_str = str(e)
            state.set_error(error_str)
        finally:
            with self.context.database.make_session() as session:
                promise = session.get(JobPromise, job_id)
                if promise is None:
                    logger.warning("Complete job #%d not found", job_id)
                elif state.error:
                    promise.error = state.error
                    state.complete()
                elif promise.valid_for.total_seconds() > 0:
                    promise.completed_at_utc = utcnow_tz()
                    state.complete()
                else:
                    try:
                        logger.debug("Deleting job #%d", job_id)
                        context = AsyncJobRuntimeContext(self.context, state, job_id, payload)
                        handler = handler_type(context)
                        handler.delete()
                    except Exception as e:
                        logger.error("Job #%d failed to delete", job_id)
                    session.delete(promise)
                    session.commit()
                    state.complete()
            del self.threads[job_id]
            del self.states[job_id]

    def __start_job(self, promise: JobPromise):
        assert promise.id is not None, "Promise must be saved to database before starting"
        if promise.id in self.threads or promise.completed_at_utc:
            if promise.completed_at_utc:
                logger.warning("Job #%d already completed", promise.id)
            else:
                logger.warning("Job #%d already running", promise.id)
            return
        handler_type = self.__resolve_handler_type(promise.issuer, promise.type)
        if handler_type is None:
            logger.warning("No handler for job #%d", promise.id)
            return
        Thread(
            target=self.__job_proc,
            args=(
                handler_type,
                Action.RUN,
                promise.id,
                promise.payload,
            ),
        ).start()

    def __resume_jobs(self):
        with self.context.database.make_session() as session:
            statement = select(JobPromise) \
                .where(JobPromise.completed_at_utc == None) \
                .where(not_(JobPromise.id.in_(self.threads)))
            promises = session.scalars(statement).all()
            for promise in promises:
                self.__start_job(promise)

    def __delete_expired_jobs(self):
        with self.context.database.make_session() as session:
            statement = select(JobPromise) \
                .where(JobPromise.completed_at_utc != None) \
                .where((JobPromise.completed_at_utc + JobPromise.valid_for) < datetime.utcnow())
            promises = session.scalars(statement).all()
            for job in promises:
                handler_type = self.__resolve_handler_type(job.issuer, job.type)
                if handler_type is not None:
                    try:
                        logger.debug("Deleting job #%d", job.id)
                        context = AsyncJobRuntimeContext(self.context, self.states.get(job.id), job.id, job.payload)
                        handler = handler_type(context)
                        handler.delete()
                    except Exception as e:
                        logger.error("Job #%d failed to delete", job.id, exc_info=e)
                session.delete(job)
