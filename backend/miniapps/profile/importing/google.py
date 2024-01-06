import asyncio
from dataclasses import dataclass
import itertools
import os.path
from typing import cast, List, Set, Coroutine
from uuid import UUID

from oauthlib.oauth2.rfc6749.tokens import OAuth2Token
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import Credentials as ExternalCredentials

from core.api.modules.rest import ApiContext
from core.asyncjob.context import AsyncJobContext
from core.asyncjob.handlers import AsyncJobHandler

from .context import ImportingContext


class GoogleImportingContext(ImportingContext):
    service: Resource

    def __init__(self, base: ImportingContext, service: Resource):
        self._extend(base)
        self.service = service


class GoogleImporter:
    NAME: str
    SERVICE: str
    VERSION: str
    SCOPES: Set[str]

    async def run(self, context: GoogleImportingContext):
        raise NotImplementedError()


@dataclass
class GoogleAuthUrl:
    url: str


class BaseGoogleImporting:
    context: ApiContext

    @classmethod
    def _google_client_secrets(cls, context: AsyncJobContext):
        return cast(str, context.env.get("GOOGLE_CLIENT_SECRETS", ""))

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
    def _google_make_service(cls, service: str, version: str, creds: Credentials|ExternalCredentials) -> Resource:
        return build(service, version, credentials=creds)

    @classmethod
    def _google_make_flow(cls, client_secrets: str, scopes: Set[str]|None = None):
        if not os.path.isfile(client_secrets):
            raise Exception("Google services aren't setup")
        if scopes is None:
            scopes = cls._google_all_scopes()
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, scopes)
        flow.redirect_uri = "http://localhost:3000/profile/import/google/callback"
        return flow
    
    @classmethod
    def encode_state(cls, options: List[str]):
        return ",".join(options)
    
    @classmethod
    def decode_state(cls, state: str):
        return {
            "options": state.split(","),
        }


class GqlGoogleImporting(BaseGoogleImporting):
    def _google_init_impl(self, options: List[str]) -> GoogleAuthUrl:
        flow = self._google_make_flow(self._google_client_secrets(self.context))
        url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            state=self.encode_state(options),
        )
        return GoogleAuthUrl(url)
    
    def _google_start_impl(self, state: str, code: str, scope: str):
        flow = self._google_make_flow(
            self._google_client_secrets(self.context),
            set(scope.split(" ")),
        )
        token: OAuth2Token = flow.fetch_token(code=code, state=state)
        self.context.asyncjobs.schedule("profile", "importing.google", {
            "state": self.decode_state(state),
            "user_id": str(self.context.user_id),
            "token_info": {
                "access": token["access_token"],
                "refresh": token.get("refresh_token"),
                "scope": token.get("scope"),
            },
        })
        return True


class GoogleImportingJob(AsyncJobHandler, BaseGoogleImporting):
    TYPE = "importing.google"
    
    dprogress: float

    def _creds_from_token(self, flow: InstalledAppFlow, token_info: dict):
        return Credentials(
            token=token_info['access'],
            refresh_token=token_info['refresh'],
            token_uri=flow.client_config["token_uri"],
            client_id=flow.client_config['client_id'],
            client_secret=flow.client_config['client_secret'],
            scopes=token_info['scope'],
        )

    async def __run_and_progress(self, importer: GoogleImporter, context: GoogleImportingContext):
        assert context.state is not None
        await importer.run(context)
        context.state.set_progress(context.state.progress + self.dprogress)

    def run(self):
        assert self.context.state is not None
        assert self.context.payload is not None
        user_id = UUID(self.context.payload["user_id"])
        flow = self._google_make_flow(self._google_client_secrets(self.context))
        credentials = self._creds_from_token(flow, self.context.payload["token_info"])
        importing_context = ImportingContext(self.context, self, user_id)

        all_importers = self._google_make_importers()
        if not all_importers:
            self.set_error("No importers found")
            return
        self.dprogress = 1.0 / len(all_importers)

        tasks: List[Coroutine] = []
        options = self.context.get_payload("state", "options")
        if options is not None:
            all_importers = [i for i in all_importers if i.NAME in options]
        for service_name, importers_by_service in itertools.groupby(all_importers, lambda i: i.SERVICE):
            for version, importers_by_version in itertools.groupby(importers_by_service, lambda i: i.VERSION):
                service = self._google_make_service(service_name, version, credentials)
                google_context = GoogleImportingContext(importing_context, service)
                for importer in importers_by_version:
                    subtask = self.__run_and_progress(importer, google_context)
                    tasks.append(subtask)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        import_task = asyncio.gather(*tasks, return_exceptions=True)
        try:
            def exc_handler(loop: asyncio.AbstractEventLoop, context: dict):
                self.set_error(context["message"])
            loop.set_exception_handler(exc_handler)
            loop.run_until_complete(import_task)
        except Exception as e:
            self.set_error(str(e))
        else:
            self.set_complete()
