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
from core.asyncjob.action import Action
from core.asyncjob.context import AsyncJobContext, AsyncJobRuntimeContext

from .context import ImportingContext


class GoogleImportingContext(ImportingContext):
    service: Resource

    def __init__(self, base: ImportingContext, service: Resource):
        self._extend(base)
        self.service = service


class GoogleImporter:
    SERVICE: str
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
    def _google_make_service(cls, service: str, creds: Credentials|ExternalCredentials) -> Resource:
        return build(service, "v3", credentials=creds)

    @classmethod
    def _google_make_flow(cls, client_secrets: str):
        if not os.path.isfile(client_secrets):
            raise Exception("Google services aren't setup")
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, cls._google_all_scopes())
        flow.redirect_uri = "http://localhost:8080/profile/importing/google"
        return flow


class GqlGoogleImporting(BaseGoogleImporting):
    def _google_init_impl(self) -> GoogleAuthUrl:
        flow = self._google_make_flow(self._google_client_secrets(self.context))
        url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
        return GoogleAuthUrl(url)


class RestGoogleImporting(BaseGoogleImporting):
    def _start_google_importing_impl(self, state: str, code: str, scope: str):
        flow = self._google_make_flow(self._google_client_secrets(self.context))
        token: OAuth2Token = flow.fetch_token(code=code)
        self.context.asyncjobs.schedule("profile", "importing.google", {
            "user_id": str(self.context.user_id),
            "token_info": {
                "access": token["access_token"],
                "refresh": token.get("refresh_token"),
                "scope": token.get("scope"),
            },
        })

    @staticmethod
    def _creds_from_token(flow: InstalledAppFlow, token_info: dict):
        return Credentials(
            token=token_info['access'],
            refresh_token=token_info['refresh'],
            token_uri=flow.client_config["token_uri"],
            client_id=flow.client_config['client_id'],
            client_secret=flow.client_config['client_secret'],
            scopes=token_info['scope'],
        )

    @staticmethod
    async def __run_and_progress(importer: GoogleImporter, context: GoogleImportingContext, dprogress: float):
        assert context.state is not None
        await importer.run(context)
        context.state.set_progress(context.state.progress + dprogress)

    @classmethod
    def google_import_job(cls, context: AsyncJobRuntimeContext):
        if context.action != Action.RUN:
            return
        assert context.state is not None
        assert context.payload is not None
        user_id = UUID(context.payload["user_id"])
        flow = cls._google_make_flow(cls._google_client_secrets(context))
        credentials = cls._creds_from_token(flow, context.payload["token_info"])
        importing_context = ImportingContext(context, user_id)
        all_importers = cls._google_make_importers()
        dprogress = 1.0 / len(all_importers)
        tasks: List[Coroutine] = []
        for service_name, importers in itertools.groupby(all_importers, lambda i: i.SERVICE):
            service = cls._google_make_service(service_name, credentials)
            google_context = GoogleImportingContext(importing_context, service)
            for importer in importers:
                subtask = RestGoogleImporting.__run_and_progress(importer, google_context, dprogress)
                tasks.append(subtask)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        import_task = asyncio.gather(*tasks, return_exceptions=True)
        try:
            loop.run_until_complete(import_task)
        except Exception as e:
            context.state.set_error(str(e))
        else:
            context.state.complete()
