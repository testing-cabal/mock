#!/usr/bin/env python
import setuptools

setuptools.setup(
    setup_requires=['pbr>=1.3', 'setuptools>=17.1'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    pbr=True)
