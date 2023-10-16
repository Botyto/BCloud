from dataclasses import dataclass
from sqlalchemy import select
from typing import List

from core.api.modules.gql import mutation, query, GqlMiniappModule
from core.asyncjob.data import JobPromise
from core.graphql.result import SuccessResult

from .google import GoogleAuthUrl, GqlGoogleImporting


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
        user_id_str = str(self.user_id)
        promises = [p for p in promises if p.payload is not None and p.payload.get("user_id") == user_id_str]
        return ImportingJobs([p.type for p in promises])

    @query()
    def google_options(self) -> ImportingOptions:
        return ImportingOptions([importer.SERVICE for importer in self._google_all_importers()])

    @mutation()
    def google_init(self, options: List[str]) -> GoogleAuthUrl:
        return self._google_init_impl(options)

    @mutation()
    def google_start(self, state: str, code: str, scope: str) -> SuccessResult:
        success = self._google_start_impl(state, code, scope)
        if success:
            payload = self.decode_state(state)
            self.log_activity("importing.google.start", payload)
        return SuccessResult(success)
