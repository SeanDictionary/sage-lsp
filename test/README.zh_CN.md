## LSP 测试指南 (pytest)

**中文 | [English](README.md)**

### 文件结构

-   [test/lsp_client.py](lsp_client.py) - LSP 客户端封装（请求/通知，响应读取）
-   [test/test_lsp_server.py](test_lsp_server.py) - Pytest 测试用例：initialize / hover / shutdown
-   [test/conftest.py](conftest.py) - Pytest 配置与路径设置

### 运行测试

```bash
pytest test/                                   # 运行全部测试并显示日志
pytest test/test_lsp_server.py                 # 运行指定文件
pytest test/test_lsp_server.py::TestLSPServer::test_hover  # 运行单个用例
```

### 添加新测试

在 [test/test_lsp_server.py](test_lsp_server.py) 中添加测试函数或类方法，使用 `lsp_client` fixture（自动启动/初始化/清理）：

```python
def test_my_feature(lsp_client):
    lsp_client.initialize()
    lsp_client.did_open(
        uri="file:///test.sage",
        language_id="sagemath",
        text="x = 1 + 1",
    )

    req_id = lsp_client.send_request("textDocument/myFeature", {
        "textDocument": {"uri": "file:///test.sage"}
    })
    response = lsp_client.read_response(expected_id=req_id)

    assert response.get("result") is not None
```

### LSPClient 快速参考

LSPClient 由一个LSPClientBase集成得到。LSPClientBase定义了必要的测试方法如下：

-   initialize() – 执行初始化握手
-   shutdown() – 优雅关闭
-   send_request(method, params=None) – 发送请求，返回请求 ID
-   send_notification(method, params=None) – 发送通知
-   read_response(expected_id=None) – 读取一条响应，自动跳过通知

LSPClient 还扩展了以下方法：

-   did_change(uri, text, version) – 发送 didChange 通知
-   did_open(uri, language_id, text, version=1) – 发送 didOpen 通知
-   hover(uri, line, character) – 请求 hover 信息
