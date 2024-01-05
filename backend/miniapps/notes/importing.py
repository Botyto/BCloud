from miniapps.profile.importing.google import GoogleImporter, GoogleImportingContext


class GoogleKeepImporter(GoogleImporter):
    SERVICE = "keep"
    SCOPES = set()

    async def run(self, context: GoogleImportingContext):
        raise NotImplementedError()
