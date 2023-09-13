from .env import Environment


class BaseContext:
    env: Environment

    def __init__(self, env: Environment):
        self.env = env

    def _extend(self, base: "BaseContext"):
        assert type(base) == type(self).__bases__[0], f"Base context of type {type(base)} cannot be extended by {type(self)}, since it doesn't inherit from it directly."
        for key, value in base.__dict__.items():
            setattr(self, key, value)
