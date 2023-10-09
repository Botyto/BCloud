from core.api.modules.gql import GqlMiniappModule
from core.api.modules.rest import RestMiniappModule

from .google import GqlGoogleImporting, RestGoogleImporting


class GqlImportingModule(GqlMiniappModule, GqlGoogleImporting):
    pass


class RestImportingModule(RestMiniappModule, RestGoogleImporting):
    pass
