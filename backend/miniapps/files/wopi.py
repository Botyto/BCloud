import base64
from dataclasses import dataclass
import json
from sqlalchemy import select
from uuid import UUID, uuid4
from typing import Dict

from .tools.files import FileManager

from core.api.modules.rest import RestMiniappModule, get, post, delete, put, ApiResponse
from core.auth.data import User
from core.auth.handlers import AuthError
from core.auth.access import AccessLevel, get_access_level_and_owner


@dataclass
class WopiEntry:
    user_id: UUID
    file_id: UUID


class WopiMapping:
    _map: Dict[str, WopiEntry]

    def __init__(self):
        self._map = {}

    def add(self, user_id: UUID, file_id: UUID):
        key = base64.b64encode(uuid4().bytes).decode("utf-8")
        value = WopiEntry(user_id, file_id)
        self._map[key] = value
        return key

    def __delitem__(self, key: str):
        del self._map[key]

    def __getitem__(self, key: str):
        return self._map[key]


class WopiContext:
    module: RestMiniappModule
    wopi: WopiEntry
    old_user_id: UUID

    def __init__(self, module: RestMiniappModule, wopi: WopiEntry):
        self.module = module
        self.wopi = wopi

    def __enter__(self):
        self.old_user_id = self.module._current_user
        self.module._current_user = self.wopi.user_id
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.module._current_user = self.old_user_id


class WopiModule(RestMiniappModule):
    _manager: FileManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            self._manager = FileManager(self.context.blobs, self.user_id, self.session)
        return self._manager

    @property
    def contents(self):
        return self.manager.contents

    @property
    def _wopi_map(self) -> WopiMapping:
        return self.miniapp.wopi  # type: ignore

    def _get_user(self, user_id: UUID):
        statement = select(User).where(User.id == user_id)
        return self.session.scalars(statement).one()

    def _get_wopi(self, token: str):
        wopi = self._wopi_map[token]
        return wopi
    
    @put("/api/files/wopi", name="files.wopi.create")
    def create(self):
        if self.current_user is None:
            raise AuthError()
        path = self.get_argument("path")
        file = self.manager.by_path(path)
        if file is None:
            raise FileNotFoundError()
        wopi_key = self._wopi_map.add(self.current_user, file.id)
        return ApiResponse(content=wopi_key)

    @delete("/api/files/wopi/(.*)", name="files.wopi.delete")
    def delete(self, token: str):
        del self._wopi_map[token]

    @get("/api/files/wopi/(.*)", name="files.wopi.metadata")
    def metadata(self, token: str):
        wopi = self._get_wopi(token)
        with WopiContext(self, wopi):
            file = self.manager.by_id(wopi.file_id)
            access, owner, _ = get_access_level_and_owner(file)
            if owner is None:
                raise NotImplementedError()
            can_write = access >= AccessLevel.PUBLIC_WRITABLE or owner.id == wopi.user_id
            user = self._get_user(wopi.user_id)
            return ApiResponse(
                content = json.dumps({
                    "BaseFileName": file.name,
                    "Size": file.size,
                    "UserId": str(wopi.user_id),
                    "UserFriendlyName": user.display_name,
                    "OwnerId": str(owner.id),
                    "UserCanNotWriteRelative": owner.id == wopi.user_id,
                    "LastModifiedTime": file.mtime_utc.isoformat(),
                    "UserCanWrite": can_write,
                }),
            )

    @get("/api/files/wopi/(.*)/contents", name="files.wopi.read")
    def read(self, token: str):
        wopi = self._get_wopi(token)
        with WopiContext(self, wopi):
            file = self.manager.by_id(wopi.file_id)
            return ApiResponse(content = self.contents.read(file))
    
    @post("/api/files/wopi/(.*)/contents", name="files.wopi.write")
    def write(self, token: str):
        wopi = self._get_wopi(token)
        with WopiContext(self, wopi):
            file = self.manager.by_id(wopi.file_id)
            content = self.request.body
            self.contents.write(file, content)
