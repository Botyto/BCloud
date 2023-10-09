from core.miniapp.miniapp import Miniapp

from .activity import ActivityModule
from .auth import AuthModule
from .edit import EditModule
from .importing.module import ImportingModule


class ProfileMiniapp(Miniapp):
    def __init__(self):
        super().__init__("profile", module_types=[
            ActivityModule,
            AuthModule,
            EditModule,
            ImportingModule,
        ])
