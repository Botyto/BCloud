Accessing BLOBs (Binary Large OBjects) could simply be done by accessing the file system.
Instead we take another approach, which is similar in syntax and usage, short to implement, but way more flexible.
We create an abstraction for some of the most commonly used modules, methods and objects related to file accesss.
This abstraction allows using the local file system, but could also store the data in any other form or location.
Fill in the BlobSettings object, call the `build_manager()` method and you'll get an object that allows using this system.
