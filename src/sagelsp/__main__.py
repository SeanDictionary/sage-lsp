import sys
import logging
from ._version import __version__
from .server import server


log = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s - %(name)s [%(levelname)s]: %(message)s"

def main():
    _config_logging(logging.INFO)
    log.info(f"Starting SageLSP {__version__}. By SeanDictionary")
    server.start_io()


def _config_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        stream=sys.stderr,
    )


if __name__ == "__main__":
    main()