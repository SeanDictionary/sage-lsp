import argparse
import sys
import logging
from sagelsp import SageAvaliable, SageVersion
from ._version import __version__
from .server import server


log = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s - %(name)s [%(levelname)s]: %(message)s"



arguments = [
    {
        'flags': ['-l', '--log'],
        'params': {
            'type': str,
            'default': 'INFO',
            'help': 'Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).',
        },
    },
    {
        'flags': ['-v', '--version'],
        'params': {
            'action': 'version',
            'version': f'SageLSP version {__version__}',
            'help': 'Show the version of SageLSP and exit.',
        }, 
    },
    {
        'flags': ['--sage'],
        'params': {
            'action': 'version',
            'version': f'Sage available: {SageAvaliable} {SageVersion}',
            'help': 'Check if Sage is available and exit.',
        },
    },
    {
        'flags': ['--clear'],
        'params': {
            'action': 'store_true',
            'help': 'Clear local symbols cache and exit.',
        },
    }
]

def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    level = logging._nameToLevel.get(args.log.upper(), logging.INFO)
    _config_logging(level)

    log.info(f"Starting SageLSP {__version__}. By SeanDictionary")
    log.info(f"Sage available: {SageAvaliable} {SageVersion}")
    log.info(f"Logging level set to {args.log.upper()}")
    log.info("-" * 40)

    if args.clear:
        from .symbols_cache import SymbolsCache
        SymbolsCache.clear()
        return

    server.start_io()


def add_arguments(parser: argparse.ArgumentParser):
    parser.description = "Sage Language Server Protocol (LSP) implementation for SageMath."
    for arg in arguments:
        parser.add_argument(*arg['flags'], **arg['params'])


def _config_logging(level=logging.INFO):
    # TODO: Support custom config
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        stream=sys.stderr,
    )


if __name__ == "__main__":
    main()