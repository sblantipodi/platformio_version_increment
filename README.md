# Platformio Version Increment
Simple version increment script for Platformio.  
  
_Platformio does not have a tool to automatically increment the version number of an app when building it or when uploading it to a microcontroller so I decided to write a script to do it._

[![GitHub version](https://img.shields.io/github/v/release/sblantipodi/platformio_version_increment.svg)](https://img.shields.io/github/v/release/sblantipodi/platformio_version_increment.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/sblantipodi/platformio_version_increment/graphs/commit-activity)
[![DPsoftware](https://img.shields.io/static/v1?label=DP&message=Software&color=orange)](https://www.dpsoftware.org)

If you like **Platformio Version Increment**, give it a star, or fork it and contribute!

[![GitHub stars](https://img.shields.io/github/stars/sblantipodi/platformio_version_increment.svg?style=social&label=Star)](https://github.com/sblantipodi/platformio_version_increment/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/sblantipodi/platformio_version_increment.svg?style=social&label=Fork)](https://github.com/sblantipodi/platformio_version_increment/network)

## Credits
- Davide Perini

## How To Use
1) From the root of your project run
```
git submodule add https://github.com/sblantipodi/platformio_version_increment.git platformio_version_increment
```

2) Add the following in your `platformio.ini`:
```
extra_scripts = 
   pre:platformio_version_increment/version_increment_pre.py
   post:platformio_version_increment/version_increment_post.py
```

3) Add `#include "Version.h"` to the top of your main source file (i.e. `main.cpp`). 

4) Build your software for your microcontroller. In the root of your project you will find two files:
- version
- include/Version.h 

The `version` file will default to `0.1.0`, but you can edit this with the version number you wish to start incrementing from.

Every completed upload will trigger a +1 on the patch number.

In the `Version.h` file (which you'll need to include in order to access the incrementing version and timestamp variables) you'll have this:
```c++
// AUTO GENERATED FILE, DO NOT EDIT THIS FILE
#ifndef VERSION
  #define VERSION "0.1.0"
#endif
#ifndef BUILD_TIMESTAMP
  #define BUILD_TIMESTAMP "2020-04-10 17:58:52.937616"
#endif
```    

Consequently, you can now have auto-incrementing VERSION and BUILD_TIMESTAMP variables you can use in your program as you wish. 

## License
This program is licensed under MIT License
