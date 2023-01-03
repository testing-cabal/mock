---
name: Bug report
about: Only report bugs here that are specific to this backport.
title: ''
labels: ''
assignees: ''

---

This package is a rolling backport of [`unittest.mock`](https://github.com/python/cpython/blob/master/Lib/unittest/mock.py). 
As such, any problems you encounter most likely need to be fixed upstream.

Before submitting an issue here, please try and reproduce the problem on the latest release of Python 3, including alphas, and replace any import from `mock` with ones from `unittest.mock`.

If the issue still occurs, then please report upstream through https://github.com/python/cpython/issues as it will need to be fixed there so that it can be backported here and released to you.

If the issue does not occur upstream, please file an issue using the template below as it may be an issue specific to the backport:

**What versions are you using?**
 - Python: [e.g. 3.7.1]
 - Mock: [e.g. 4.0.2]
 - Operating System: [e.g.Linux, macOS, Windows]

**What happened?**

<!-- 
A clear and concise description of what the problem is, including full tracebacks and code being executed  
-->

**What were you hoping to happen instead?**
