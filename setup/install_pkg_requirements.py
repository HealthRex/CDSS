#!/usr/bin/python
"""
Script for installing non-pip package requirements.
Because pip is platform agnostic, default to using pip whenever possible.
However, there will be cases when pip is insufficient (e.g. installing gcc on AMAZON_LINUX).
"""

import platform
from subprocess import call

MAC_OSX = 'mac-osx'
AMAZON_LINUX = 'amazon-linux'

# Use a single dictionary to define all the platform-specific installation commands.
INSTALLATION_COMMANDS = {
    'gcc': {
        AMAZON_LINUX: ['sudo', 'yum', 'install', 'gcc']
    },
    'matplotlib': {
        AMAZON_LINUX: ['sudo', 'python', '-m', 'pip', 'install', '-U', 'matplotlib'],
        MAC_OSX: ['sudo', 'python', '-m', 'pip', 'install', '-U', 'matplotlib']
    }
}

def identify_platform():
    if 'amzn' in platform.platform():
        return AMAZON_LINUX
    else:
        return MAC_OSX

def install_requirements():
    platform = identify_platform()
    for requirement in INSTALLATION_COMMANDS.keys():
        if INSTALLATION_COMMANDS[requirement].get(platform):
            command = INSTALLATION_COMMANDS[requirement][platform]
            call(command)

install_requirements()
