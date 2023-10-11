from typing import Dict, Type

from .action import Action
from .context import AsyncJobRuntimeContext

from ..data.blobs.address import Address


class AsyncJobHandler:
    TYPE: str
    context: AsyncJobRuntimeContext

    def __init__(self, context: AsyncJobRuntimeContext):
        self.context = context

    def set_progress(self, progress: float):
        assert self.context.state is not None
        self.context.state.set_progress(progress)

    def set_complete(self):
        assert self.context.state is not None
        self.context.state.complete()

    def set_error(self, error: str):
        assert self.context.state is not None
        self.context.state.set_error(error)

    def temp_file_addr(self, *parts: str):
        return Address("asyncjobs", Address.join_keys(str(self.context.job_id), *parts), True)

    def trigger(self, action: Action):
        match action:
            case Action.RUN:
                return self.run()
            case Action.DELETE:
                return self.delete()
            case Action.CANCEL:
                return self.cancel()
            case _:
                raise ValueError("Unkown asyncjob action")

    def run(self):
        raise NotImplementedError()
    
    def delete(self):
        pass

    def cancel(self):
        pass


class IssuerMap:
    issuer: str
    handler_types: Dict[str, Type[AsyncJobHandler]]

    def __init__(self, app_id: str):
        self.issuer = app_id
        self.handler_types = {}

    def add(self, type: str, handler_type: Type[AsyncJobHandler]):
        assert type not in self.handler_types, f"Job type {self.issuer}.{type} already registered"
        self.handler_types[type] = handler_type

    def resolve(self, type: str) -> Type[AsyncJobHandler]|None:
        return self.handler_types.get(type)


class JobHandlers:
    by_issuer: Dict[str, IssuerMap]

    def __init__(self):
        self.by_issuer = {}

    def add(self, issuer: str, type: str, handler_type: Type[AsyncJobHandler]):
        issuer_handlers = self.by_issuer.get(issuer)
        if issuer_handlers is None:
            issuer_handlers = IssuerMap(issuer)
            self.by_issuer[issuer] = issuer_handlers
        issuer_handlers.add(type, handler_type)

    def resolve(self, issuer: str, type: str) -> Type[AsyncJobHandler]|None:
        issuer_handlers = self.by_issuer.get(issuer)
        if issuer_handlers is None:
            return None
        return issuer_handlers.handler_types.get(type)
