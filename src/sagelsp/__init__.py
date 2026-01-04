import pluggy
from ._version import __version__
from .enumeration import *

try:
    import sage # type: ignore
    SageAvaliable = True
except ImportError:
    SageAvaliable = False

NAME = "sagelsp"

hookspec = pluggy.HookspecMarker(NAME)
hookimpl = pluggy.HookimplMarker(NAME)

__all__ = [
    "__version__",
]

