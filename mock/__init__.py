from __future__ import absolute_import
import mock.mock as _mock
from mock.mock import *

__version__ = '4.0.0b1'
version_info = tuple(int(p) for p in __version__.split('.'))


__all__ = ('__version__', 'version_info') + _mock.__all__
