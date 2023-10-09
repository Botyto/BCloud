from core.api.modules.gql import mutation, GqlMiniappModule
from core.api.modules.rest import get, RestMiniappModule

from .google import GoogleAuthUrl, GqlGoogleImporting, RestGoogleImporting


class ImportingModule(GqlMiniappModule, GqlGoogleImporting):
    @mutation()
    def google_init(self) -> GoogleAuthUrl:
        return self._google_init_impl()


class RestImportingModule(RestMiniappModule, RestGoogleImporting):
    @get("/profile/importing/google/(.*)")
    def start_google_importing(self, auth_code: str):
        return self._start_google_importing_impl(auth_code)
