from ..context import DataContext


class Migrations:
    context: DataContext

    def __init__(self, context: DataContext):
        self.context = context

    def init(self):
        pass

    def new(self):
        pass

    def update(self):
        pass

    def uninstall(self):
        pass
