from core.miniapp.miniapp import Miniapp

from .auth import AuthModule


class ProfileMiniapp(Miniapp):
    def __init__(self):
        super().__init__("profile", module_types=[
            AuthModule,
        ])
