from dataclasses import dataclass
import itertools
import os.path
from typing import Callable, cast, List, Set

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import Credentials as ExternalCredentials


from core.api.modules.gql import GqlMiniappModule, mutation
from core.graphql.result import SuccessResult


@dataclass
class GoogleImporter:
    service: str
    scopes: Set[str]
    callback: Callable[[Resource], None]


@dataclass
class GoogleAuthUrl:
    url: str


class ImportingModule(GqlMiniappModule):
    def _make_google_service(self, service: str, creds: Credentials|ExternalCredentials) -> Resource:
        return build(service, "v3", credentials=creds)

    def _make_google_flow(self):
        google_client_secerts = cast(str, self.context.env.get("GOOGLE_CLIENT_SECRETS", ""))
        if not os.path.isfile(google_client_secerts):
            raise Exception("Google services aren't setup")
        all_importers: List[GoogleImporter] = []
        self.context.msg.emit("importing_gather_google", all_importers)
        if not all_importers:
            raise Exception("Nothing to import from Google")
        assert all(isinstance(i, GoogleImporter) for i in all_importers), "Importers must be GoogleImporter"
        all_scopes = set()
        for importer in all_importers:
            all_scopes.update(importer.scopes)
        return InstalledAppFlow.from_client_secrets_file(google_client_secerts, all_scopes)

    @mutation()
    def google_init(self) -> GoogleAuthUrl:
        flow = self._make_google_flow()
        flow.redirect_uri = "localhost:3000/profile/importing/google"
        url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
        return GoogleAuthUrl(url)

    @mutation()
    def google_auth(self, auth_code: str) -> SuccessResult:
        flow = self._make_google_flow()
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        all_importers: List[GoogleImporter] = []
        self.context.msg.emit("importing_gather_google", all_importers)
        by_service = itertools.groupby(all_importers, lambda i: i.service)
        for service_name, importers in by_service:
            service = self._make_google_service(service_name, creds)
            for importer in importers:
                importer.callback(service)
        return SuccessResult()
