"""
====================
MangaDex API Wrapper
====================

An API wrapper for `mangadex.org <https://mangadex.org>`_'s public API. Credit goes to
`mangadex.org <https://mangadex.org>`_ for providing a very well documented public API. Please use this code within
reason and do not send an unnecessary amount of requests to MangaDex; I have implemented simple measures under the hood
make sure this is avoided if unintentional.

License: GNU GPLv3 (check the 'LICENCE' file in source directory).
"""


from .chapters import MangaChapters
from .manga import MangaSearch

from ._errors import *

__version__ = "1.0.0"
__author__ = "boddz"
__licence__ = "GNU GPLv3"
