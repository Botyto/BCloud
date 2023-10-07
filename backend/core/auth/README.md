This module implements the authentication logic.
Users have their own object in the database of type `User`.
Each login also creates it's own object of type `UserSession`.
All `UserSession` objects are associated with a `Device`.
The session stores some sensitive data on the backend + some sensitive data on the client. Any useable sensitive data cannot be obtained without having both the client and the backend data.
All object IDs are UUIDs to improve security.
Passwords are hashed using the bcrypt library.
There's an `UserManager` class that can be used to easily manager users (register, login, logout, etc.).
All request handlers that need access to an authenticated user (which should be almost all of them), must inherit from `AuthHandlerMixin`, which will automatically authenticate the user and prepare auth data for easy access.

There is an ownership and sharing system implemented - each object can have a single owner. Following the owner chain we must always end up at a `User` object.
Owner foreign keys must be marked explicitly by adding an info={"owner": True} to the column.

At this point sessions aren't very secure - only the session ID is sent to the user and used for authentication.
Encryption is not implemented at this point, but should be done using the DEK/KEK scheme.

Frontend/API authentication can be done through either an Authorization cookkie or header using the Bearer scheme.
