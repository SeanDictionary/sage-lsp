from typing import Any, Dict
from lspclientbase import LSPClientBase
import sys


class LSPClient(LSPClientBase):
    def hover(self, uri: str, line: int, character: int) -> Dict[str, Any]:
        """
        Request hover information

        Args:
            uri: Document URI
            line: Line number (0-based)
            character: Character offset (0-based)

        Returns:
            Hover response result
        """
        request_id = self.send_request("textDocument/hover", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character}
        })

        response = self.read_response(expected_id=request_id)
        return response.get("result")

    def did_open(self, uri: str, language_id: str, text: str, version: int = 1):
        """
        Notify server that document is opened

        Args:
            uri: Document URI
            language_id: Language identifier
            text: Document content
            version: Document version
        """
        DEBUG = """
========== Code Text ==========
{code_text}
===============================

"""
        print(DEBUG.format(code_text=text), file=sys.stderr)
        self.send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": language_id,
                "version": version,
                "text": text
            }
        })

    def did_change(self, uri: str, text: str, version: int = 1):
        """
        Notify server that document is changed

        Args:
            uri: Document URI
            text: New document content
            version: Document version
        """
        self.send_notification("textDocument/didChange", {
            "textDocument": {
                "uri": uri,
                "version": version
            },
            "contentChanges": [
                {
                    "text": text
                }
            ]
        })

    def formatting(self, uri: str):
        """
        Request document formatting

        Args:
            uri: Document URI
            text: Document content
            version: Document version

        Returns:
            List of TextEdits for formatting
        """
        request_id = self.send_request("textDocument/formatting", {
            "textDocument": {"uri": uri},
            "options": {
                "tabSize": 4,
                "insertSpaces": True
            }
        })

        response = self.read_response(expected_id=request_id)
        return response.get("result")

    def definition(self, uri: str, line: int, character: int):
        """
        Request definition locations

        Args:
            uri: Document URI
            line: Line number (0-based)
            character: Character offset (0-based)

        Returns:
            Definition response result
        """
        request_id = self.send_request("textDocument/definition", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character}
        })

        response = self.read_response(expected_id=request_id)
        return response.get("result")

    def type_definition(self, uri: str, line: int, character: int):
        """
        Request type definition locations

        Args:
            uri: Document URI
            line: Line number (0-based)
            character: Character offset (0-based)

        Returns:
            Type Definition response result
        """
        request_id = self.send_request("textDocument/typeDefinition", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character}
        })

        response = self.read_response(expected_id=request_id)
        return response.get("result")

    def completion(self, uri: str, line: int, character: int):
        """
        Request completion items

        Args:
            uri: Document URI
            line: Line number (0-based)
            character: Character offset (0-based)

        Returns:
            Completion response result (list of CompletionItems or CompletionList)
        """
        request_id = self.send_request("textDocument/completion", {
            "textDocument": {"uri": uri},
            "position": {"line": line, "character": character}
        })

        response = self.read_response(expected_id=request_id)
        return response.get("result")
