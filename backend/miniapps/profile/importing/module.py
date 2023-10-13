from dataclasses import dataclass
from sqlalchemy import select
from typing import List

from core.api.modules.gql import mutation, query, GqlMiniappModule
from core.api.modules.rest import get, RestMiniappModule
from core.asyncjob.data import JobPromise

from .google import GoogleAuthUrl, GqlGoogleImporting, RestGoogleImporting


@dataclass
class ImportingJobs:
    jobs: List[str]


@dataclass
class ImportingOptions:
    options: List[str]


class ImportingModule(GqlMiniappModule, GqlGoogleImporting):
    @query()
    def running(self) -> ImportingJobs:
        statement = select(JobPromise) \
            .where(JobPromise.issuer == "profile") \
            .where(JobPromise.type.startswith("importing"))
        promises = self.session.scalars(statement).all()
        promises = [p for p in promises if p.payload is not None and p.payload.get("user_id") == self.user_id]
        return ImportingJobs([p.type for p in promises])

    @query()
    def google_options(self) -> ImportingOptions:
        return ImportingOptions([importer.SERVICE for importer in self._google_all_importers()])

    @mutation()
    def google_init(self) -> GoogleAuthUrl:
        return self._google_init_impl()


class RestImportingModule(RestMiniappModule, RestGoogleImporting):
    @get("/profile/importing/google")
    def start_google_importing(self, state: str, code: str, scope: str):
        return self._start_google_importing_impl(state, code, scope)
