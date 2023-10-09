import asyncio
from dataclasses import dataclass
import itertools
import os.path
from typing import cast, List, Set, Coroutine
from uuid import UUID

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import Credentials as ExternalCredentials

from core.api.modules.rest import ApiContext
from core.asyncjob.action import Action
from core.asyncjob.context import AsyncJobRuntimeContext

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
    def _google_init_impl(self) -> GoogleAuthUrl:
        flow = self._google_make_flow(self._google_client_secrets)
        flow.redirect_uri = "https://bisserkr.me/profile/importing/google"
        url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
        return GoogleAuthUrl(url)


class RestGoogleImporting(BaseGoogleImporting):
    def _start_google_importing_impl(self, auth_code: str):
        flow = self._google_make_flow(self._google_client_secrets)
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        self.context.asyncjobs.schedule("profile", "importing.google", {
            "user_id": str(self.context.user_id),
            "creds": creds,
        })

    @staticmethod
    async def __run_and_progress(importer: GoogleImporter, context: GoogleImportingContext, dprogress: float):
        assert context.state is not None
        await importer.run(context)
        context.state.set_progress(context.state.progress + dprogress)

    @classmethod
    def _google_import(cls, context: AsyncJobRuntimeContext):
        if context.action != Action.RUN:
            return
        assert context.state is not None
        assert context.payload is not None
        user_id = UUID(context.payload["user_id"])
        creds = context.payload["creds"]
        importing_context = ImportingContext(context, user_id)
        all_importers = cls._google_make_importers()
        dprogress = 1.0 / len(all_importers)
        tasks: List[Coroutine] = []
        for service_name, importers in itertools.groupby(all_importers, lambda i: i.SERVICE):
            service = cls._google_make_service(service_name, creds)
            google_context = GoogleImportingContext(importing_context, service)
            for importer in importers:
                subtask = RestGoogleImporting.__run_and_progress(importer, google_context, dprogress)
                tasks.append(subtask)
        import_task = asyncio.gather(*tasks, return_exceptions=True)
        try:
            asyncio.get_event_loop().run_until_complete(import_task)
        except Exception as e:
            context.state.set_error(str(e))
        else:
            context.state.complete()
