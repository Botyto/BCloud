This module implements the authentication logic.
Users have their own object in the database of type `User`.
Each login also creates it's own object of type `UserSession`.
The session stores some sensitive data on the backend + some sensitive data on the frontend.
All object IDs are UUIDs to improve security.
Passwords are hashed using the bcrypt library.
There's an `UserManager` class that can be used to manager users.