import pluggy
from ._version import __version__
from .enumeration import *

NAME = "sagelsp"

hookspec = pluggy.HookspecMarker(NAME)
hookimpl = pluggy.HookimplMarker(NAME)

__all__ = [
    "__version__",
]

