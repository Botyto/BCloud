import time

from .env import Environment


class BaseContext:
    init_time: float
    env: Environment

    def __init__(self, env: Environment):
        self.init_time = time.time()
        self.env = env

    def _extend(self, base: "BaseContext"):
        assert type(base) == type(self).__bases__[0], f"Base context of type {type(base)} cannot be extended by {type(self)}, since it doesn't inherit from it directly."
        for key, value in base.__dict__.items():
            setattr(self, key, value)
