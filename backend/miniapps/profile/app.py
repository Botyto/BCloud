from core.miniapp.miniapp import Miniapp, ModuleRegistry, AsyncjobRegistry

from .activity import ActivityModule
from .auth import AuthModule
from .edit import EditModule
from .importing.module import ImportingModule, RestImportingModule
from .importing.google import GoogleImportingJob


class ProfileMiniapp(Miniapp):
    def __init__(self):
        super().__init__("profile",
            ModuleRegistry(ActivityModule),
            ModuleRegistry(AuthModule),
            ModuleRegistry(EditModule),
            ModuleRegistry(ImportingModule),
            ModuleRegistry(RestImportingModule),
            AsyncjobRegistry("importing.google", GoogleImportingJob),
        )
