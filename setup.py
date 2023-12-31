import os
import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent.resolve()

PACKAGE_NAME = "ixBrowser"
AUTHOR = "Alan Ting & Ontisme"
AUTHOR_EMAIL = "alanting0716@gmail.com"
URL = "https://github.com/ontisme/ixBrowser"
DOWNLOAD_URL = "https://pypi.org/project/ixBrowser/"

LICENSE = "MIT"
VERSION = os.getenv("TAG", "0.0.0")
DESCRIPTION = "A SDK for ixBrowser"
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf8")
LONG_DESC_TYPE = "text/markdown"

with open((HERE / "requirements.txt"), encoding="utf8", errors='ignore') as f:
    requirements = f.read()
INSTALL_REQUIRES = [s.strip() for s in requirements.split("\n")]

with open((HERE / "dev_requirements.txt"), encoding="utf8", errors='ignore') as f:
    dev_requirements = f.read()
EXTRAS_REQUIRE = {"dev": [s.strip() for s in dev_requirements.split("\n")]}

CLASSIFIERS = [f"Programming Language :: Python :: 3.{str(v)}" for v in range(7, 12)]
PYTHON_REQUIRES = ">=3.7"

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    packages=find_packages(),
    classifiers=CLASSIFIERS,
)