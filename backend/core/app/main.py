from core.data.context import DataContext


class AppContext(DataContext):
    pass


class App:
    context: AppContext

    def __init__(self, context: AppContext):
        self.context = context

    def run(self):
        print("Hello world!")
