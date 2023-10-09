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



class ImportingModule(GqlMiniappModule):
    def _make_google_service(self, service: str, creds: Credentials|ExternalCredentials) -> Resource:
        return build(service, "v3", credentials=creds)

    @mutation()
    def google(self) -> SuccessResult:
        google_client_secerts = cast(str, self.context.env.get("GOOGLE_CLIENT_SECRETS", ""))
        if not os.path.isfile(google_client_secerts):
            raise Exception("Google services aren't setup")
        all_importers: List[GoogleImporter] = []
        self.context.msg.emit("importing_gather_google", all_importers)
        if not all_importers:
            return SuccessResult()
        assert all(isinstance(i, GoogleImporter) for i in all_importers), "Importers must be GoogleImporter"
        all_scopes = set()
        for importer in all_importers:
            all_scopes.update(importer.scopes)
        flow = InstalledAppFlow.from_client_secrets_file(google_client_secerts, all_scopes)
        creds = flow.run_local_server(port=0)
        by_service = itertools.groupby(all_importers, lambda i: i.service)
        for service_name, importers in by_service:
            service = self._make_google_service(service_name, creds)
            for importer in importers:
                importer.callback(service)
        return SuccessResult()
