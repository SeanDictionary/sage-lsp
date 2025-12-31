"""Pytest 配置文件 - 定义全局 fixture 和配置"""

import sys
import os
import pytest
from lspclient import LSPClient

# 添加 test 目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

@pytest.fixture
def client():
    lsp = LSPClient([sys.executable, "-m", "sagelsp"])
    lsp.start()
    lsp.initialize()  # Auto-initialize for all tests
    
    yield lsp
    
    try:
        if lsp.initialized:
            lsp.shutdown()
    finally:
        lsp.stop()