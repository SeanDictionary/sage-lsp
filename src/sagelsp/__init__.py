import pluggy
from platformdirs import user_cache_dir
from ._version import __version__
from .enumeration import *


NAME = "sagelsp"
CachePath = user_cache_dir(appname="sagelsp", appauthor="SeanDictionary")

hookspec = pluggy.HookspecMarker(NAME)
hookimpl = pluggy.HookimplMarker(NAME)

try:
    import sage # type: ignore
    from .symbols_cache import SymbolsCache, SymbolStatus
    SageAvaliable = True
except ImportError:
    SageAvaliable = False

__all__ = [
    "__version__",
]

