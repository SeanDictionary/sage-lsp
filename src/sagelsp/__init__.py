import pluggy
from platformdirs import user_cache_dir
from ._version import __version__

NAME = "sagelsp"
CachePath = user_cache_dir(appname="sagelsp", appauthor="SeanDictionary")

hookspec = pluggy.HookspecMarker(NAME)
hookimpl = pluggy.HookimplMarker(NAME)

try:
    import sage # type: ignore
    from sage.env import SAGE_VERSION, SAGE_DATE
    from .symbols_cache import SymbolsCache, SymbolStatus
    SageAvaliable = True
    SageVersion = f"{SAGE_VERSION} ({SAGE_DATE})"
except ImportError:
    SageAvaliable = False
    SageVersion = ""

__all__ = [
    "__version__",
]

