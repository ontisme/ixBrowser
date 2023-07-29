ixBrowser
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

