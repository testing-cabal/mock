import warnings

def examine_warnings(func):
    with warnings.catch_warnings(record=True) as ws:
        func(ws)
