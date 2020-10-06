#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = "0.0.1"


setup(
    name="python-circleci-package-boilerplate",
    version=VERSION,
    description="Your description here",
    long_description="see repo for readme",
    url="https://github.com/15five/python-circleci-package-boilerplate",
    author="Your name here",
    author_email="Your email here",
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="insert your keywords here",
    packages=find_packages(),
    install_requires=["requests==2.22.0",],
    python_requires=">=3.6",
)
