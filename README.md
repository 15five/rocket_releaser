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
