"""
SageMath Language Server implementation.

This module implements the Language Server Protocol for SageMath,
providing IDE features such as completion, hover, diagnostics, etc.
"""

import logging
from typing import Optional

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    CompletionList,
    CompletionParams,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    Hover,
    HoverParams,
    MarkupContent,
    MarkupKind,
)

from .sage_features import SageFeatures

logger = logging.getLogger(__name__)

# Global sage features instance
sage_features = SageFeatures()


async def did_open(ls, params: DidOpenTextDocumentParams):
    """Handle text document open event."""
    logger.info(f"Opened document: {params.text_document.uri}")


async def did_change(ls, params: DidChangeTextDocumentParams):
    """Handle text document change event."""
    logger.debug(f"Document changed: {params.text_document.uri}")


async def did_save(ls, params: DidSaveTextDocumentParams):
    """Handle text document save event."""
    logger.info(f"Document saved: {params.text_document.uri}")


async def completions(ls, params: CompletionParams) -> Optional[CompletionList]:
    """
    Provide completion suggestions for SageMath code.
    
    Args:
        ls: Language server instance
        params: Completion parameters including position and document
        
    Returns:
        List of completion items or None
    """
    try:
        # Access document through the protocol's workspace
        document = ls.protocol.workspace.text_documents[params.text_document.uri]
        position = params.position
        
        # Get completions from SageMath features
        items = sage_features.get_completions(
            document.source,
            position.line,
            position.character
        )
        
        return CompletionList(
            is_incomplete=False,
            items=items
        )
    except Exception as e:
        logger.error(f"Error in completion: {e}", exc_info=True)
        return None


async def hover(ls, params: HoverParams) -> Optional[Hover]:
    """
    Provide hover information for symbols.
    
    Args:
        ls: Language server instance
        params: Hover parameters including position and document
        
    Returns:
        Hover information or None
    """
    try:
        # Access document through the protocol's workspace
        document = ls.protocol.workspace.text_documents[params.text_document.uri]
        position = params.position
        
        # Get hover information from SageMath features
        hover_text = sage_features.get_hover(
            document.source,
            position.line,
            position.character
        )
        
        if hover_text:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=hover_text
                )
            )
        return None
    except Exception as e:
        logger.error(f"Error in hover: {e}", exc_info=True)
        return None


def create_server():
    """Create and configure the language server."""
    from pygls.protocol import LanguageServerProtocol, default_converter
    from pygls.server import JsonRPCServer
    
    class SageLanguageServer(JsonRPCServer):
        """SageMath Language Server."""
        
        def __init__(self):
            # Set server name and version before calling parent __init__
            self.name = "sage-lsp"
            self.version = "0.1.0"
            
            super().__init__(LanguageServerProtocol, default_converter)
            
            # Register handlers using the decorator pattern
            self.protocol.fm.feature(TEXT_DOCUMENT_DID_OPEN)(did_open)
            self.protocol.fm.feature(TEXT_DOCUMENT_DID_CHANGE)(did_change)
            self.protocol.fm.feature(TEXT_DOCUMENT_DID_SAVE)(did_save)
            self.protocol.fm.feature(TEXT_DOCUMENT_COMPLETION)(completions)
            self.protocol.fm.feature(TEXT_DOCUMENT_HOVER)(hover)
    
    return SageLanguageServer()


def main():
    """Main entry point for the language server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SageMath Language Server")
    parser.add_argument(
        "--tcp",
        action="store_true",
        help="Use TCP server instead of stdio"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for TCP server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=2087,
        help="Port for TCP server (default: 2087)"
    )
    parser.add_argument(
        "--log-file",
        help="Path to log file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if args.log_file:
        logging.basicConfig(
            level=log_level,
            format=log_format,
            filename=args.log_file,
            filemode="a"
        )
    else:
        logging.basicConfig(level=log_level, format=log_format)
    
    logger.info("Starting SageMath Language Server")
    
    # Create server
    server = create_server()
    
    # Start the server
    if args.tcp:
        logger.info(f"Starting TCP server on {args.host}:{args.port}")
        server.start_tcp(args.host, args.port)
    else:
        logger.info("Starting stdio server")
        server.start_io()


if __name__ == "__main__":
    main()
