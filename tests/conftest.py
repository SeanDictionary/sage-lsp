"""Pytest 配置文件 - 定义全局 fixture 和配置"""

import sys
import os
import pytest
from color import Color
from sagelsp import SageAvaliable
from lspclient import LSPClient

# add src directory to sys.path for imports
sys.path.insert(0, os.path.dirname(__file__))

@pytest.fixture
def client():
    lsp = LSPClient([sys.executable, "-m", "sagelsp", "--log", "DEBUG"])
    lsp.start()
    lsp.initialize()  # Auto-initialize for all tests
    
    yield lsp
    
    try:
        if lsp.initialized:
            lsp.shutdown()
    finally:
        lsp.stop()

def pytest_sessionstart(session):
    """add info at session start"""
    pass

def pytest_report_header(config):
    """add info to the report header"""
    return [
        f"Sage Available: {Color.green(str(SageAvaliable)) if SageAvaliable else Color.red(str(SageAvaliable))}",
    ]