# Platformio Version Increment
Simple version increment script for Platformio.

Platformio does not have a tool to automatically increment the version number of an app when building it or when uploading it to a microcontroller so I decided to write a script to do it.


To use it please add this line in your platformio.ini
```
extra_scripts = pre:platformio_version_increment/version_increment.py
```

from the root of your project run
```
git submodule add git@github.com:sblantipodi/platformio_version_increment.git platformio_version_increment
```


