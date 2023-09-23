```
Now, there is an official library available. Please refer to it by visiting the following link:
```
[Official ixBrowser Python Library](https://github.com/ixspyinc/ixbrowser-local-api-python)


Unoffical ixBrowser
=======

Client for ixBrowser API written in Python

Installation
============

```
pip install ixBrowser
```

Usage
=====

```python
from ixBrowser import ixBrowser

ixbrowser = IxBrowser()

# Get the list of profiles
ixbrowser.api_browser_list()

# Open the browser
ixbrowser.api_browser_open(1)

# Close the browser
ixbrowser.api_browser_close(1)
```

Build
=====
```bash
pip install twine setuptools

python setup.py sdist bdist_wheel
twine upload  --skip-existing dist/*
```
