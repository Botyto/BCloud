import asyncio
from dataclasses import dataclass
import itertools
import os.path
from typing import cast, List, Set, Coroutine

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import Credentials as ExternalCredentials

from core.api.modules.gql import mutation
from core.api.modules.rest import get, ApiContext
from core.asyncjob.handlers import Action, State


class GoogleImporter:
    SERVICE: str
    SCOPES: Set[str]

    async def run(self, service: Resource, payload: dict):
        raise NotImplementedError()


@dataclass
class GoogleAuthUrl:
    url: str


class BaseGoogleImporting:
    context: ApiContext

    @property
    def _google_client_secrets(self):
        return cast(str, self.context.env.get("GOOGLE_CLIENT_SECRETS", ""))

    @classmethod
    def _google_all_importers(cls):
        return GoogleImporter.__subclasses__()
    
    @classmethod
    def _google_all_scopes(cls):
        all_scopes = set()
        for importer in cls._google_all_importers():
            all_scopes.update(importer.SCOPES)
        return all_scopes
    
    @classmethod
    def _google_make_importers(cls):
        return [i() for i in cls._google_all_importers()]

    @classmethod
    def _google_make_service(cls, service: str, creds: Credentials|ExternalCredentials) -> Resource:
        return build(service, "v3", credentials=creds)

    @classmethod
    def _google_make_flow(cls, client_secrets: str):
        if not os.path.isfile(client_secrets):
            raise Exception("Google services aren't setup")
        return InstalledAppFlow.from_client_secrets_file(client_secrets, cls._google_all_scopes())


class GqlGoogleImporting(BaseGoogleImporting):
    @mutation()
    def google_init(self) -> GoogleAuthUrl:
        flow = self._google_make_flow(self._google_client_secrets)
        flow.redirect_uri = "localhost:3000/profile/importing/google"
        url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
        return GoogleAuthUrl(url)


class RestGoogleImporting(BaseGoogleImporting):
    @get("/profile/importing/google/(.*)")
    def start_google_importing(self, auth_code: str):
        flow = self._google_make_flow(self._google_client_secrets)
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        self.context.asyncjobs.schedule("profile", "importing.google", {
            "user_id": self.context.user_id,
            "creds": creds,
        })

    @staticmethod
    async def __wrapper(state: State, dprogress: float, importer: GoogleImporter, service: Resource, payload: dict):
        await importer.run(service, payload)
        state.set_progress(state.progress + dprogress)

    @classmethod
    def _google_import(cls, action: Action, state: State|None, id: int, payload: dict):
        if action != Action.RUN:
            return
        assert state is not None
        creds = payload["creds"]
        all_importers = cls._google_make_importers()
        by_service = itertools.groupby(all_importers, lambda i: i.SERVICE)
        tasks: List[Coroutine] = []
        dprogress = 1.0 / len(all_importers)
        for service_name, importers in by_service:
            service = cls._google_make_service(service_name, creds)
            for importer in importers:
                wrapper = RestGoogleImporting.__wrapper(state, dprogress, importer, service, payload)
                tasks.append(wrapper)
        import_task = asyncio.gather(*tasks, return_exceptions=True)
        try:
            asyncio.get_event_loop().run_until_complete(import_task)
        except Exception as e:
            state.set_error(str(e))
        else:
            state.complete()
