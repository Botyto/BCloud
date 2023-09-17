This folder contains code for the "core" or the engine/system of the backend.
That is - base code that can be reused for a similar project - database management, HTTP server, API tools, authentication & security, etc.

Major components (ordered by their dependencies):
- `data` - tools for dealing with data persistance - be it an SQL database, file system/store or something else.
- `app` - base container for the rest of the system. You can have more than one running at once.
- `msg` and `cronjob` - Global communication and task scheduling systems.
- `asyncjob` - System for executing jobs that take a long time (many minutes or even hours) and are prone to interruption.
- `miniapp` - System for easily separating, enabling/disabling and versioning miniapps within the server.
- `http` - the HTTP server part of the system.
- `auth` - Authentication and authorization built on top of the HTTP server.

The way modules decide how to behave is done using context objects.
Example: the `App` object uses an `AppContext`.
The context object is created before being sent to the `App` and shouldn't be modified ever.
At places where you have to create/extend a context, the program is designed to be able to "branch".
