#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = "0.0.3"


setup(
    name="rocket_releaser",
    version=VERSION,
    description="Script for release notes and labeling upon deploys",
    long_description="see repo for readme",
    url="https://github.com/15five/rocket_releaser",
    author="15Five",
    author_email="caleb@15five.com",
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
    keywords="release-notes release-automation",
    packages=find_packages(),
    install_requires=[
        "jira==2.0.0",
        "github3.py==1.2.0",
        "gitdb2==3.0.1",
        "slacker==0.9.65",
        "requests==2.22.0",
    ],
    python_requires=">=3.6",
)
