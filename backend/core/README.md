This folder contains code for the "core" or the engine/system of the backend.
That is - base code that can be reused for a similar project - database management, HTTP server, API tools, authentication & security, etc.

Major components:
- `data` - tools for dealing with data persistance - be it an SQL database, file system/store or something else.
- `app` - base container for the rest of the system. You can have more than one running at once.
- 