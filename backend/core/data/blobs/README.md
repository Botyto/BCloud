Accessing BLOBs (Binary Large OBjects) could simply be done by accessing the file system.
Instead we take another approach, which is similar in syntax and usage, short to implement, but way more flexible.
We create an abstraction for some of the most commonly used modules, methods and objects related to file accesss.
This abstraction allows using the local file system, but could also store the data in any other form or location.
Fill in the BlobSettings object, call the `build_manager()` method and you'll get an object that allows using this system.

There are a few implementations of the Blobs manager:
- There's an abstract base class
- The FS blobs manager (env: `BLOB_FS_ROOT`) that stores files on the local machine
- SQL blobs manager (env: `BLOB_SQL`) that will store the blobs on the SQL database - this is not recommended because it's slow and restricted in blob address length
- AWS S3 blobs manager (env: `BLOB_S3`; required permissions: ListBucket, Get/Put/Replicate/DeleteObject)
