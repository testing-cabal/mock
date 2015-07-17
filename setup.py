#!/usr/bin/env python
import setuptools


def _parse_requirements(fname):
    ''' Return the content of the specified file except for the lines starting
    with a ``#``.
    It will also split the line having a `;` on this character and keep only the
    first part.
    '''
    ret = []
    with open(fname) as stream:
        for line in stream.readlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ';' in line:
                line = line.split(';', 1)[0].strip()
            if line:
                ret.append(line)
    return ret


setuptools.setup(
    setup_requires=['pbr>=1.3'],
    install_requires=_parse_requirements('requirements.txt'),
    pbr=True)
