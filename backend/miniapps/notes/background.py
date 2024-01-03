from core.asyncjob.context import AsyncJobRuntimeContext
from core.asyncjob.handlers import AsyncJobHandler


class NotePostprocessor:
    context: AsyncJobRuntimeContext

    def should_run(self) -> bool:
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()


class PostprocessHandler(AsyncJobHandler):
    def select_preprocessor(self):
        postprocessor_classes = NotePostprocessor.__subclasses__()
        for cls in postprocessor_classes:
            postprocessor = cls(self.context)
            if postprocessor.should_run():
                return postprocessor

    def run(self):
        postprocessor = self.select_preprocessor()
        if postprocessor is not None:
            postprocessor.run()
