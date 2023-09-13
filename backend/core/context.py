class BaseContext:
    @classmethod
    def extend(cls, base: "BaseContext", **kwargs):
        assert type(base) == cls.__bases__[0], f"Base context of type {type(base)} cannot be extended by {cls}, since it doesn't inherit from it directly."
        result = cls()
        for key, value in base.__dict__.items():
            setattr(result, key, value)
        for key, value in kwargs.items():
            setattr(result, key, value)
        return result
