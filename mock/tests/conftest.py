import six


def pytest_ignore_collect(path):
    if 'py3' in path.basename and six.PY2:
        return True
