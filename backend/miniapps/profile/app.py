from core.miniapp.miniapp import Miniapp, MiniappAsyncJob

from .activity import ActivityModule
from .auth import AuthModule
from .edit import EditModule
from .importing.module import ImportingModule, RestImportingModule
from .importing.google import GoogleImportingJob


class ProfileMiniapp(Miniapp):
    def __init__(self):
        super().__init__("profile",
            module_types=[
                ActivityModule,
                AuthModule,
                EditModule,
                ImportingModule,
                RestImportingModule,
            ],
            async_jobs=[
                MiniappAsyncJob("importing.google", GoogleImportingJob)
            ],
        )
