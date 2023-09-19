from ..auth.context import AuthContext


class ApiContext(AuthContext):
    def __init__(self, base: AuthContext):
        self._extend(base)
