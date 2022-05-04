#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import sys


if sys.argv[-1] == 'setup.py':
    print("To install, run 'python setup.py install'")
    print()

setuptools.setup(
    name="cogmodel",
    version=1.0,
    description="Cognitive Models Environment",
    long_description="This package provides a simple 2D gridworld " \
        "implementation designed for the Applied Cognitive Modeling seminar of " \
        "the WS 2018/2019 held by the Social Cognitive Systems Group of " \
        "Bielefeld University.",
    maintainer="Jan Pöppel",
    maintainer_email="jpoeppel@techfak.uni-bielefeld.de",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        # 'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    packages=[
            "cogmodel"
        ],
    package_dir={'cogmodel': 'cogmodel'},
    package_data={'cogmodel': ['Conditions/*']},
    install_requires = [
            "matplotlib"
        ],
    )
