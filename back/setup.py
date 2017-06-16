#!/usr/bin/env python
# -*- coding: utf-8 -*-

import versiontools_support
from setuptools import setup, find_packages
from distutils.command.sdist import sdist as _sdist
import os
import shutil

class mysdist(_sdist):
    """Custom sdist."""

    def copy_parent_files(self):
        """Copy parent files to current directory."""
        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(current_dir)
        for fil in ['README.md', 'LICENSE']:
            shutil.copy(os.path.join(parent_dir, fil), current_dir)

    """Custom hook."""
    def run(self):
        self.copy_parent_files()
        _sdist.run(self)


setup(
    name = 'taiga-contrib-cas-auth',
    version = ":versiontools:taiga_contrib_cas_auth:",
    description = "The Taiga plugin for cas authentication",
    long_description = "../README.md",
    keywords = 'taiga, cas, auth, plugin',
    author = 'Rose Louis',
    author_email = 'lrose@sante-aquitaine.fr',
    url = '',
    license = 'AGPL',
    include_package_data = True,
    packages = find_packages(),
    install_requires=[
        'python-cas >= 1.2.0'
    ],
    setup_requires = [
        'versiontools >= 1.9',
        'setuptools-markdown'
    ],
    classifiers = [
        "Programming Language :: Python",
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'
    ],
    cmdclass = {'sdist' : mysdist}
)
