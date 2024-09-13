#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = "0.1.1a"

setup(
    name="rocket_releaser",
    version=VERSION,
    description="Script for release notes and labeling upon deploys",
    long_description="See repo for README.md",
    url="https://github.com/15five/rocket_releaser",
    author="15Five",
    author_email="devops@15five.com",
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
        "Programming Language :: Python :: 3.12",
    ],
    keywords="release-notes release-automation",
    packages=find_packages(),
    install_requires=["gitdb2>=4", "github3.py>=4", "jira>=3", "slacker"],
    python_requires=">=3.9",
)
