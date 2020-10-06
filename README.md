# python-circleci-package-boilerplate [![CircleCI](https://circleci.com/gh/15five/python-circleci-package-boilerplate.svg?style=svg&circle-token=f6c8494ec308088a8a65fe79e366763b02b38d9b)](https://circleci.com/gh/15five/python-circleci-package-boilerplate) [![PyPI version](https://badge.fury.io/py/python-circleci-package-boilerplate.svg)](https://badge.fury.io/py/python-circleci-package-boilerplate)
boilerplate repo you can use as a base for your python package.

## Features:
* Package directory structure already laid out
* **FULL** CI/CD through circleci with the works (black linting, pip caching, tests against multiple python versions, test summary, coverage results, automatic package deploy each push to master)
* Makefile and other sensible files and configuration already present

## To Use:
1. Copy Repo
2. Replace all instances of "python-circleci-package-boilerplate" with your package name
3. Replace "healthchecks_manager" folder name with package name. Do search/replace as well.
4. Go over setup.py and configure it to your liking
4. Replace code & tests
5. Register project w/ circleci
6. Set CIRCLE_TOKEN and PYPI_PASSWORD env vars
7. Replace "caleb15" in `.circleci/config.yml` with your pypi username for package publishing
8. Replace readme

## License: [Unlicense](https://unlicense.org/)

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>
