# Procedure for new miniapp setup
This is written while creating the `photos` miniapp, so that will be used as an example.

## Setting up the miniapp
Create the `photos` folder.
Create a `app.py` file inside.
Define a class that inherits from `core.miniapp.miniapp.Miniapp`.
In the `__init__()` method call the super construction with a unique `id` and fill in the `dependencies`.
In the `core/entry/server.py` file there are lists that mention every app. Add your newly created class to those.

## Setting up the data model
Next you'll need a way to persistently store user data.
Create a `data.py` file.
Define SQLAlchemy declarative models that inherit from `core.data.sql.database.Model`.
There are a few helper python modules to aid in the creation of models:
 - `core.data.sql.columns` - contains SQL data types, useful constants, functions useful for column defaults, commonly used SQLAlchemy functions for describing columns, useful functions for data validation.
 - `core.data.sql.slugs` - contains an implementation for slug columns. You'll need the `SLUG_LENGTH` constant and the `slug_info()` function.
 - `core.auth.access` - contains an implementation of per-model sharing/access level information. You'll need the `AccessLevel` enum and the `access_info()` function.
 - `core.auth.owner` - contains logic for automated ownership checking. Use the `owner_info()` function from it.
 - `core.auth.data` - contains data models commonly used in relationships - `User`, `Login`, `Activity`
Note: take care not to confuse `uuid.UUID` with `core.data.sql.columns.UUID`. To help avoid this, do `from uuid import UUID as PyUUID`.

Common imports are:
```Python
from core.auth.access import AccessLevel
from core.auth.data import User
from core.data.sql.columns import Boolean, DateTime, Enum, Float, Integer, String, UUID, STRING_MAX, utcnow_tz
from core.data.sql.columns import mapped_column, relationship, Mapped
from core.data.sql.database import Model
from core.data.sql.slugs import SLUG_LENGTH, slug_info
```

For readability, make sure all models begin with a common prefix, making them easily distinguishable.
When the data model is done, run the `Migrations: new` configuration to create a new migration.

## Implement the backend
Create a folder named `tools`.
Inside should reside classes that implement (preferrably) all operations that may be done in the miniapp.
These classes should be designed such that they can be easily reused by other classes of the miniapp, or by other miniapps that wish to integrate with this one.
For the `photos` example, the assets tool will reuse tools from the `files` miniapp to store it's photos.
All tool classes must be instanciated before being used (no class methods).
These tools often have the following constructor parameters:
 - `user_id` (nullable) - useful for knowing which items to enumerate and to discard foreign items.
 - `context` - context within which to work. A common type is `core.asyncjob.context.AsyncJobContext`
 - `session` - an SQLAlchemy session to reuse when dealing with the database.
 - `service` - if the tool is used for service purposes, as opposed to serving a user request.
Only the `service` parameter is present in all tools. It is accompanied by a classmethod named `for_service` which instantiates the tool for working in "service" mode.
In the `photos` miniapp example, it's useful to have the following tools:
 - `importing` deals with postprocessing of recently imported assets
 - `files` for interoping with the `files` miniapp for persistent file storage.
 - `album` for dealing with albums (CRUD, etc.)
 - `assets` for dealing with assets (CRUD, etc.)
 - In the future, when implementing photo editing, it might be useful to create a new tool specifically for that.

## Implement the API
The API is implemented through "miniapp modules".
These come in a few types:
 - `core.api.modules.gql.GqlMiniappModule` - Used with the `query`, `mutation` and `subscription` decorators for it's methods.
 - `core.api.modules.rest.RestMiniappModule` - Used with the `get`, and `post` decorators.
 - `core.api.modules.api.ApiMiniappModule` - A blank slate class inherited by the other two.
Module classes are a declarative way of constructing the API.
They don't have a custom constructor and don't hold state between requests.
They should roughly correspond to the tool classes and methods, since the operations in those are mostly related to user interactions.
Adding `from core.api.pages import PagesInput, PagesResult` is often useful for implementing paginations.

When a module is complete, it must be registered in the miniapp class.
This is done using the `core.miniapp.miniapp.ModuleRegistry` class.
Other such classes exist for other things that the app depends on, such as:
 - `ClassRegistry` - does nothing, just references a class so it gets loaded
 - `MsgRegistry` - registers a global message handler
 - `AsyncjobRegistry` - registers an asyncjob handler
 - `SqlEventRegistry` - for handling SQLAlchemy events

## Implement the frontend
...
