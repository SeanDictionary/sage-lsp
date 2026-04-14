import pluggy
from platformdirs import user_cache_dir
from ._version import __version__

NAME = "sagelsp"
CachePath = user_cache_dir(appname="sagelsp", appauthor="SeanDictionary")

hookspec = pluggy.HookspecMarker(NAME)
hookimpl = pluggy.HookimplMarker(NAME)

try:
    import sage # type: ignore
    from sage.env import SAGE_VERSION, SAGE_DATE    # type: ignore
    from .symbols_cache import SymbolsCache, SymbolStatus
    SageAvaliable = True
    SageVersion = f"{SAGE_VERSION} ({SAGE_DATE})"
except ImportError:
    SageAvaliable = False
    SageVersion = ""

LANGUAGE_ID = "sagemath"

__all__ = [
    "__version__",
    "hookspec",
    "hookimpl",
    "SageAvaliable",
    "SageVersion",
    "LANGUAGE_ID",
    "CachePath",
]

