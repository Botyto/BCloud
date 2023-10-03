Accessing BLOBs (Binary Large OBjects) could simply be done by accessing the file system.
Instead we take another approach, which is similar in syntax and usage, short to implement, but way more flexible.
We create an abstraction for some of the most commonly used modules, methods and objects related to file accesss.
This abstraction allows using the local file system, but could also store the data in any other form or location.
Fill in the BlobSettings object, call the `build_manager()` method and you'll get an object that allows using this system.

There are a few implementations of the Blobs manager:
First off - there's a base class that only throws NotImplemented errors.
Then there's the FS blobs manager that stores files on the local machine.
There is an SQL blobs manager that will store the blobs on the SQL database - this is not recommended because it's slow and restricted in blob address length.
