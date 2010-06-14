import warnings

def examine_warnings(func):
    def wrapper():
        with warnings.catch_warnings(record=True) as ws:
            func(ws)
    return wrapper
