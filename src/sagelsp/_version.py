from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sage-lsp")
except PackageNotFoundError:
    __version__ = "dev"