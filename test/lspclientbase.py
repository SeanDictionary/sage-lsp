import json
import subprocess
import sys
from typing import Any, Dict, Optional, List
from color import Color

class LSPClientBase:    
    def __init__(self, server_command: List[str]):
        """
        Initialize LSP client
        
        Args:
            server_command: start command for LSP server, e.g. ["pylsp"]
        """
        self.server_command = server_command
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.initialized = False
    
    def start(self):
        """Start LSP server process"""
        print(f"{Color.BOLD}Starting server: {' '.join(self.server_command)}{Color.RESET}", file=sys.stderr)
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,  # Let server logs go to terminal stderr
        )
    
    def stop(self):
        """Stop LSP server process"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
    
    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        send JSON-RPC request and return request ID
        
        Args:
            method: LSP method name
            params: request parameters
            
        Returns:
            request ID
        """
        if method == "shutdown":
            print(file=sys.stderr)
        if not self.process:
            raise RuntimeError("Server not started")
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        if params:
            request["params"] = params
        
        content = json.dumps(request)
        message = f"Content-Length: {len(content)}\r\n\r\n{content}"
        
        print(f"{Color.BLUE}→ Sending request [{self.request_id}]: {method}{Color.RESET}", file=sys.stderr)
        self.process.stdin.write(message.encode())
        self.process.stdin.flush()
        
        return self.request_id
    
    def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """
        Send JSON-RPC notification
        
        Args:
            method: LSP method name
            params: request parameters
        """
        if not self.process:
            raise RuntimeError("Server not started")
        
        notification = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params is not None:  # Check for None instead of truthiness
            notification["params"] = params
        
        content = json.dumps(notification)
        message = f"Content-Length: {len(content)}\r\n\r\n{content}"
        
        print(f"{Color.BLUE}→ Sending notification: {method}{Color.RESET}", file=sys.stderr)
        self.process.stdin.write(message.encode())
        self.process.stdin.flush()
    
    def _read_message(self) -> Dict[str, Any]:
        """Read one LSP message (response or notification)."""
        if not self.process:
            raise RuntimeError("Server not started")

        headers = {}
        while True:
            line = self.process.stdout.readline().decode().strip()
            if not line:
                break
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value

        content_length = int(headers.get("Content-Length", 0))
        content = self.process.stdout.read(content_length).decode()
        message = json.loads(content)

        if "id" in message:
            print(f"{Color.GREEN}← Received response [{message['id']}]{Color.RESET}", file=sys.stderr)
        else:
            print(f"{Color.GREEN}← Received notification: {message.get('method', 'unknown')}{Color.RESET}", file=sys.stderr)

        return message

    def read_response(self, expected_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Read response; automatically skip notifications until matching expected_id.

        Args:
            expected_id: Expected request ID; if None, return first message with id.
        """
        while True:
            message = self._read_message()

            # Only care about responses with id, skip notifications
            if "id" not in message:
                continue

            if expected_id is not None and message.get("id") != expected_id:
                # Not target response, continue reading
                continue

            return message
    
    def initialize(self, root_uri: Optional[str] = None) -> Dict[str, Any]:
        """
        Initialize LSP server
        
        Args:
            root_uri: workspace 根 URI
            
        Returns:
            Initialize response result
        """
        request_id = self.send_request("initialize", {
            "processId": None,
            "rootUri": root_uri,
            "capabilities": {}
        })
        
        response = self.read_response(expected_id=request_id)
        
        if "result" not in response:
            raise RuntimeError("Initialize response missing result")
        
        # Send initialized notification
        self.send_notification("initialized", {})
        self.initialized = True
        
        print(f"{Color.GREEN}✓ Initialization successful{Color.RESET}", file=sys.stderr)
        return response["result"]
    
    def shutdown(self):
        """Execute graceful shutdown"""
        if not self.initialized:
            return
        
        request_id = self.send_request("shutdown")
        response = self.read_response(expected_id=request_id)
        
        # Send exit notification
        self.send_notification("exit")
        
        print(f"{Color.GREEN}✓ Server shutdown complete{Color.RESET}", file=sys.stderr)
        self.initialized = False

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self):
        """Context manager exit"""
        try:
            if self.initialized:
                self.shutdown()
        finally:
            self.stop()
