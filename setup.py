#!/usr/bin/env python
import os
from setuptools import setup, find_packages

setup(
    name='KeychainIO',
    version='0.0.1',
    author='Jeff Lindsay',
    author_email='progrium@gmail.com',
    description='Modern key management in the cloud',
    license='MIT',
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    url="http://github.com/progrium/keychain.io",
    packages=find_packages(),
    install_requires=['Flask', 'boto'],
)

