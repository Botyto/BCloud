from asyncio import Event


class JobCancelledError(Exception):
    pass


class State:
    progress: float = 0.0
    completed: bool = False
    cancelled: bool = False
    event: Event
    error: str|None = None

    def __init__(self):
        self.event = Event()

    def set_progress(self, progress: float):
        assert 0.0 <= progress and progress <= 1.0
        if self.completed:
            return
        if self.cancelled:
            raise JobCancelledError()
        self.progress = progress
        self.event.set()

    def complete(self):
        self.completed = True
        self.event.set()

    def cancel(self):
        self.cancelled = True
        self.event.set()

    def set_error(self, error: str):
        self.error = error

    @property
    def finished(self):
        return self.completed or self.cancelled

    async def wait(self):
        await self.event.wait()

    def reset(self):
        self.event.clear()
